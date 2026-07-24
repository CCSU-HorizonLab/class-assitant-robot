"""Schemas package."""
from __future__ import annotations

from .auth import (
    LoginRequest,
    RegisterRequest,
    EmailCodeRequest,
    UserCreateRequest,
    StatusUpdateRequest,
    AISummaryRequest,
)
from .interaction import (
    InteractionResultPayload,
    ApiResponse,
)
from .device import (
    HeartbeatRequest,
    DeviceResponse,
    DeviceListResponse,
)

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "EmailCodeRequest",
    "UserCreateRequest",
    "StatusUpdateRequest",
    "AISummaryRequest",
    "InteractionResultPayload",
    "ApiResponse",
    "HeartbeatRequest",
    "DeviceResponse",
    "DeviceListResponse",
]
