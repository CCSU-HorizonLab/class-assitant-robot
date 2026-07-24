"""Routers package."""
from __future__ import annotations

from .auth import router as auth_router, pages_router
from .ingestion import router as ingestion_router
from .teacher import router as teacher_router
from .admin import router as admin_router
from .dashboard import router as dashboard_router
from .device import router as device_router, start_heartbeat_checker, stop_heartbeat_checker

__all__ = [
    "auth_router",
    "pages_router",
    "ingestion_router",
    "teacher_router",
    "admin_router",
    "dashboard_router",
    "device_router",
    "start_heartbeat_checker",
    "stop_heartbeat_checker",
]
