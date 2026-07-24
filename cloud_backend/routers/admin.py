"""Admin routing for page rendering."""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from .auth import AUTH_COOKIE_NAME, require_page_user
from ..views import (
    build_admin_home_html,
    build_admin_classrooms_html,
    build_admin_devices_html,
    build_admin_teachers_html,
    build_admin_results_html,
    build_admin_ingestion_html,
    build_forbidden_html,
)

router = APIRouter()


def _login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


def _forbidden_response() -> HTMLResponse:
    return HTMLResponse(content=build_forbidden_html(), status_code=403)


@router.get("/admin", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_home(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.7 admin platform overview."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_home_html(user))


@router.get("/admin/classrooms", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_classrooms_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.7 admin classroom overview."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_classrooms_html(user))


@router.get("/admin/teachers", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_teachers_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.7 admin teacher overview."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_teachers_html(user))


@router.get("/admin/results", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_results_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.7 all-platform classroom results view."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_results_html(user))


@router.get("/admin/ingestion", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_ingestion_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the Phase 2.8 three-side ingestion status view."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_ingestion_html(user))


@router.get("/admin/devices", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_devices_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Render the IoT device status monitoring page."""
    try:
        user = require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return HTMLResponse(content=build_admin_devices_html(user))


@router.get("/admin/trends", response_class=HTMLResponse, tags=["Admin Pages"])
async def admin_trends_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)) -> HTMLResponse:
    """Redirect the retired admin trend page to classroom data."""
    try:
        require_page_user(auth_token, required_role="admin")
    except HTTPException as exc:
        return _login_redirect() if exc.status_code == 401 else _forbidden_response()
    return RedirectResponse(url="/admin/results", status_code=302)
