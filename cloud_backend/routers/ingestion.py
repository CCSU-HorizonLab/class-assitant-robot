"""Ingestion routers for receiving classroom feedback and videos."""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, Header, HTTPException, Request, UploadFile

from ..config import settings
from ..schemas import ApiResponse, InteractionResultPayload

router = APIRouter()

SUPPORTED_VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".ogg"}


def _extract_payload_dict(body: Any) -> Dict[str, Any]:
    """兼容直接 payload 和 envelope 两种提交格式。"""
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="请求体必须是 JSON 对象")

    if "payload" in body and isinstance(body["payload"], dict):
        return body["payload"]
    return body


def _check_api_key(api_key: Optional[str]) -> None:
    """API Key 简单校验。"""
    if not settings.require_api_key:
        return

    if not api_key:
        raise HTTPException(status_code=401, detail="缺少鉴权请求头：{0}".format(settings.api_key_header))
    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="API Key 无效")


def _validate_business_fields(payload: InteractionResultPayload) -> None:
    """业务字段校验。"""
    if settings.classroom_id_required and not payload.classroom_id:
        raise HTTPException(status_code=422, detail="classroom_id 为必填字段")
    if settings.source_host_required and not payload.source.source_host:
        raise HTTPException(status_code=422, detail="source_host 为必填字段")


def _store_validated_payload(
    payload_dict: Dict[str, Any],
    request_id: str,
    client_host: str,
) -> tuple[InteractionResultPayload, Path]:
    """Validate, raw-persist, and index a classroom analysis payload."""
    from ..main import raw_repository, repository, logger

    payload = InteractionResultPayload.model_validate(payload_dict)
    _validate_business_fields(payload)

    payload_dict_for_storage = payload.model_dump(mode="json")
    saved_path = raw_repository.save(payload_dict_for_storage)

    if repository is not raw_repository:
        try:
            repository.save(payload_dict_for_storage, source_path=saved_path, source_kind="raw")
        except Exception as exc:  # pragma: no cover - keep raw persistence as the hard floor
            logger.exception("Query repository indexing failed after raw persistence | request_id=%s | error=%s", request_id, exc)

    logger.info(
        "接收到课堂交互结果 | request_id=%s | client=%s | classroom_id=%s | window_id=%s | saved_path=%s",
        request_id,
        client_host,
        payload.classroom_id,
        payload.analysis_id,
        saved_path,
    )

    return payload, saved_path


def _safe_name_token(value: str, fallback: str = "upload") -> str:
    """Return a path-safe token without trusting client-provided paths."""
    token = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "")).strip("._-")
    return token or fallback


def _safe_upload_filename(filename: Optional[str]) -> str:
    """Normalize an uploaded video filename and reject unsafe suffixes."""
    original_name = Path(filename or "classroom-video.mp4").name
    original_path = Path(original_name)
    suffix = original_path.suffix.lower()
    if suffix not in SUPPORTED_VIDEO_SUFFIXES:
        raise HTTPException(status_code=400, detail="仅支持 mp4/webm/mov/ogg 视频文件")
    stem = _safe_name_token(original_path.stem, fallback="classroom-video")
    return f"{stem}{suffix}"


def _unique_video_path(upload_dir: Path, analysis_id: str, safe_filename: str) -> Path:
    """Build a non-overwriting video path under the configured upload directory."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(safe_filename).suffix.lower()
    stem = Path(safe_filename).stem
    analysis_token = _safe_name_token(analysis_id, fallback="analysis")
    base_name = f"{analysis_token}__{stem}{suffix}"
    candidate = upload_dir / base_name
    if candidate.exists():
        candidate = upload_dir / f"{analysis_token}__{stem}__{uuid.uuid4().hex[:8]}{suffix}"

    resolved_dir = upload_dir.resolve()
    resolved_parent = candidate.parent.resolve()
    if resolved_parent != resolved_dir:
        raise HTTPException(status_code=400, detail="视频文件名不合法")
    return candidate


async def _save_video_upload(video_file: UploadFile, analysis_id: str) -> tuple[Path, str]:
    """Save an uploaded classroom video and return its local path plus /uploads URL."""
    safe_filename = _safe_upload_filename(video_file.filename)
    target_path = _unique_video_path(settings.video_upload_dir, analysis_id, safe_filename)
    try:
        with target_path.open("wb") as file_obj:
            while True:
                chunk = await video_file.read(1024 * 1024)
                if not chunk:
                    break
                file_obj.write(chunk)
    except OSError as exc:
        if target_path.exists():
            target_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="视频文件保存失败") from exc

    if not target_path.exists() or target_path.stat().st_size <= 0:
        target_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="上传视频文件为空")

    return target_path, f"/uploads/{target_path.name}"


async def _read_result_json_from_form(request: Request, fallback_text: Optional[str]) -> Dict[str, Any]:
    """Read result_json from multipart as either a file field or a string field."""
    form = await request.form()
    result_json_part = form.get("result_json")

    if hasattr(result_json_part, "read"):
        raw_bytes = await result_json_part.read()
        raw_text = raw_bytes.decode("utf-8-sig")
    elif isinstance(result_json_part, str):
        raw_text = result_json_part
    elif fallback_text:
        raw_text = fallback_text
    else:
        raise HTTPException(status_code=400, detail="缺少 result_json 表单字段")

    try:
        body = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="result_json 不是合法 JSON") from exc

    return _extract_payload_dict(body)


def _payload_with_video_url(payload_dict: Dict[str, Any], video_url: str) -> Dict[str, Any]:
    """Inject the cloud video URL while preserving existing video metadata."""
    updated_payload = dict(payload_dict)
    video_info = dict(updated_payload.get("video") or {})
    video_info["video_url"] = video_url
    updated_payload["video"] = video_info
    return updated_payload


@router.post("/api/interaction-results", response_model=ApiResponse, tags=["Ingestion API"])
async def receive_interaction_results(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    """接收本地推送的课堂交互统计结果。"""
    from ..main import logger

    request_id = str(uuid.uuid4())
    client_host = request.client.host if request.client else "unknown"

    _check_api_key(x_api_key)

    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        logger.warning("请求 JSON 解析失败 | request_id=%s | client=%s | error=%s", request_id, client_host, exc)
        raise HTTPException(status_code=400, detail="请求体不是合法 JSON")

    payload_dict = _extract_payload_dict(body)
    _, saved_path = _store_validated_payload(payload_dict, request_id, client_host)

    return ApiResponse(
        success=True,
        message="课堂交互结果接收成功",
        request_id=request_id,
        saved_path=str(saved_path),
    )


@router.post("/api/interaction-results/with-video", tags=["Ingestion API"])
async def receive_interaction_results_with_video(
    request: Request,
    video_file: UploadFile = File(...),
    result_json_text: Optional[str] = Form(default=None),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> Dict[str, Any]:
    """接收本地端自动上传的课堂视频和分析 JSON 数据包。"""
    request_id = str(uuid.uuid4())
    client_host = request.client.host if request.client else "unknown"

    _check_api_key(x_api_key)

    payload_dict = await _read_result_json_from_form(request, result_json_text)
    prevalidated_payload = InteractionResultPayload.model_validate(payload_dict)
    _validate_business_fields(prevalidated_payload)

    video_path, video_url = await _save_video_upload(video_file, prevalidated_payload.analysis_id)
    payload_with_video = _payload_with_video_url(payload_dict, video_url)
    payload, saved_path = _store_validated_payload(payload_with_video, request_id, client_host)

    return {
        "success": True,
        "message": "课堂视频与分析结果接收成功",
        "request_id": request_id,
        "saved_path": str(saved_path),
        "video_url": video_url,
        "video_path": str(video_path),
        "analysis_id": payload.analysis_id,
    }
