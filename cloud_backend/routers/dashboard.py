"""Dashboard routing for page rendering and latest results APIs."""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Cookie, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from .auth import AUTH_COOKIE_NAME, optional_page_user
from ..views import build_results_center_html, latest_result_or_404, build_forbidden_html

router = APIRouter()


def _login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


def _forbidden_response() -> HTMLResponse:
    return HTMLResponse(content=build_forbidden_html(), status_code=403)


def _authorized_classroom_ids(user: Dict[str, Any]) -> Optional[set[str]]:
    from ..main import repository

    if user.get("role") == "admin":
        return None
    if not hasattr(repository, "get_workbench_classrooms"):
        return set()
    return {str(item.get("classroom_id")) for item in repository.get_workbench_classrooms(user_id=user.get("user_id")) if item.get("classroom_id")}


def _dashboard_allowed(user: Dict[str, Any], classroom_id: Optional[str], result_id: Optional[str]) -> bool:
    from ..main import repository

    allowed = _authorized_classroom_ids(user)
    if allowed is None:
        return True
    if result_id and hasattr(repository, "get_workbench_result_detail"):
        detail = repository.get_workbench_result_detail(result_id)
        if detail is None:
            return True
        return str(detail.get("classroom_id") or "") in allowed
    if classroom_id:
        return classroom_id in allowed
    return True


@router.get("/api/latest-interaction-result", tags=["Dashboard"])
async def latest_interaction_result(classroom_id: Optional[str] = None) -> Dict[str, Any]:
    """Return the latest available classroom interaction result."""
    from ..main import repository

    payload, source_path, source_kind = latest_result_or_404(repository, classroom_id=classroom_id)
    return {
        "success": True,
        "source_kind": source_kind,
        "source_path": str(source_path),
        "result": payload,
    }


@router.get("/api/recent-interaction-results", tags=["Dashboard"])
async def recent_interaction_results(
    limit: int = Query(default=5, ge=1, le=100),
    classroom_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Return recent classroom interaction results with optional classroom filtering."""
    from ..main import repository

    if status not in (None, "", "raw", "reviewed", "archived"):
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    results = repository.recent_results(limit=limit, classroom_id=classroom_id, status=status)
    return {
        "success": True,
        "limit": limit,
        "classroom_id": classroom_id,
        "status": status,
        "fallback_to_sample": bool(results and results[0]["source_kind"] == "sample"),
        "results": [
            {
                "source_kind": item["source_kind"],
                "source_path": str(item["source_path"]),
                "summary": item["summary"],
                "result": item["payload"],
            }
            for item in results
        ],
    }


@router.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard(
    classroom_id: Optional[str] = None,
    status: Optional[str] = None,
    result_id: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100),
    auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME),
) -> HTMLResponse:
    """Render a teacher-facing classroom results center."""
    from ..main import repository

    user = optional_page_user(auth_token)
    if not user:
        return _login_redirect()
    if not _dashboard_allowed(user, classroom_id, result_id):
        return _forbidden_response()
    if status not in (None, "", "raw", "reviewed", "archived"):
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    if user.get("role") == "teacher" and not classroom_id:
        if result_id and hasattr(repository, "get_workbench_result_detail"):
            detail = repository.get_workbench_result_detail(result_id)
            classroom_id = (detail or {}).get("classroom_id") or classroom_id
        if not classroom_id:
            allowed = _authorized_classroom_ids(user) or set()
            classroom_id = sorted(allowed)[0] if allowed else classroom_id
    if result_id and hasattr(repository, "detail_result"):
        selected = repository.detail_result(result_id)
        payload, source_path, source_kind = selected if selected is not None else latest_result_or_404(repository, classroom_id=classroom_id)
    else:
        payload, source_path, source_kind = latest_result_or_404(repository, classroom_id=classroom_id)
    if hasattr(repository, "get_workbench_recent"):
        recent_results = repository.get_workbench_recent(
            limit=limit,
            classroom_id=classroom_id,
            status=status,
            user_id=user.get("user_id") if user.get("role") == "teacher" else None,
        )
    else:
        recent_results = repository.recent_results(limit=limit, classroom_id=classroom_id, status=status)
    return HTMLResponse(
        content=build_results_center_html(
            payload,
            source_path,
            source_kind,
            recent_results,
            classroom_id,
            status,
            limit,
            result_id,
            user,
        )
    )
