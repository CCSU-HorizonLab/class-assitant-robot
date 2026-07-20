"""Teacher routing for page rendering."""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from .auth import AUTH_COOKIE_NAME, require_page_user
from ..views import (
    build_teacher_home_html,
    build_teacher_reports_html,
    build_teacher_results_html,
    build_forbidden_html,
)

router = APIRouter()


def _login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


def _forbidden_response() -> HTMLResponse:
    return HTMLResponse(content=build_forbidden_html(), status_code=403)


@router.get("/teacher", response_class=HTMLResponse, tags=["Teacher Pages"])
async def teacher_home(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.6 teacher home page."""
    try:
        user = require_page_user(auth_token, required_role="teacher")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_teacher_home_html(user))


@router.get("/teacher/results", response_class=HTMLResponse, tags=["Teacher Pages"])
async def teacher_results_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.6 classroom records center."""
    try:
        user = require_page_user(auth_token, required_role="teacher")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_teacher_results_html(user))


@router.get("/teacher/trends", response_class=HTMLResponse, tags=["Teacher Pages"])
async def teacher_trends_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Redirect the retired trend page to the report center."""
    try:
        require_page_user(auth_token, required_role="teacher")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return RedirectResponse(url="/teacher/reports", status_code=302)


@router.get("/teacher/reports", response_class=HTMLResponse, tags=["Teacher Pages"])
async def teacher_reports_page(
    result_id: Optional[str] = None,
    auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME),
) -> HTMLResponse:
    """Render the Phase 3.0 classroom report list or detail page."""
    try:
        user = require_page_user(auth_token, required_role="teacher")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_teacher_reports_html(user, result_id=result_id))
