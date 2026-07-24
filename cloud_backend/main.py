"""课堂交互分析系统云端接收服务入口。"""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import (
    auth_router,
    pages_router,
    ingestion_router,
    teacher_router,
    admin_router,
    dashboard_router,
    device_router,
    start_heartbeat_checker,
    stop_heartbeat_checker,
)
from .utils.logging_utils import setup_logging
from .services import FileResultRepository, build_query_repository

logger = setup_logging(settings.log_level)
raw_repository = FileResultRepository(settings)
repository = build_query_repository(settings, raw_repository)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用启动和关闭逻辑。"""
    settings.ensure_directories()
    logger.info("Cloud query repository backend=%s", getattr(repository, "backend_name", "unknown"))
    logger.info("云端接收服务启动完成，数据目录：%s", settings.data_dir)
    start_heartbeat_checker()
    yield
    await stop_heartbeat_checker()
    logger.info("云端接收服务已关闭")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="用于接收本地课堂交互分析结果并落盘/入库的云端服务",
    lifespan=lifespan,
)

# 允许跨域请求 (CORS)，解决前端与边缘端跨域通信问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(ingestion_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(dashboard_router)
app.include_router(device_router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), check_dir=False), name="static")

SUPPORTED_VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".ogg"}


def _mount_video_uploads() -> None:
    """Mount the configured video upload directory as the /uploads static route.

    Uploaded classroom videos are always stored in ``settings.video_upload_dir``,
    so that directory MUST be the one served under /uploads.  If the directory
    cannot be created the route is left unmounted and a clear warning is emitted.
    """
    try:
        settings.video_upload_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.warning(
            "Video uploads directory cannot be created: %s | error=%s — /uploads route disabled",
            settings.video_upload_dir, exc,
        )
        return

    app.mount("/uploads", StaticFiles(directory=str(settings.video_upload_dir)), name="uploads")
    logger.info("Mounted video uploads directory at /uploads: %s", settings.video_upload_dir)


def _mount_local_captures() -> None:
    """Mount the local captures delivery directory so raw_video_path entries
    that point to on-disk capture files become playable via /captures."""
    captures_dir = settings.video_local_captures_dir
    if captures_dir.exists() and captures_dir.is_dir():
        app.mount("/captures", StaticFiles(directory=str(captures_dir)), name="captures")
        logger.info("Mounted local captures directory at /captures: %s", captures_dir)
    else:
        logger.info(
            "Local captures directory not found (%s); /captures route is disabled",
            captures_dir,
        )


_mount_video_uploads()
_mount_local_captures()




@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """统一 HTTP 异常响应。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "request_id": str(uuid.uuid4()),
        },
    )


if __name__ == "__main__":
    import uvicorn
    # 使用 "cloud_backend.main:app" 以适配包内相对导入的路径定位
    uvicorn.run("cloud_backend.main:app", host="0.0.0.0", port=8011, reload=True)
