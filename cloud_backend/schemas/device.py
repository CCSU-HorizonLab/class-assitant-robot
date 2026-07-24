"""Device heartbeat and management schemas."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class HeartbeatRequest(BaseModel):
    """Pi → Cloud heartbeat payload."""
    device_mac: str = Field(..., min_length=12, max_length=17)
    device_name: Optional[str] = Field(default=None, max_length=100)
    classroom_name: Optional[str] = Field(default=None, max_length=100)
    device_type: Optional[str] = Field(default="real", max_length=20)
    cpu_percent: Optional[float] = None
    mem_percent: Optional[float] = None
    disk_percent: Optional[float] = None
    temperature: Optional[float] = None
    timestamp: Optional[int] = None


class DeviceResponse(BaseModel):
    """Device info returned to admin frontend."""
    id: int
    device_name: str
    device_mac: Optional[str]
    classroom_name: Optional[str]
    device_type: str
    device_status: str
    last_heartbeat: Optional[str]
    cpu_percent: Optional[float]
    mem_percent: Optional[float]
    disk_percent: Optional[float]
    temperature: Optional[float]
    capture_count: int
    is_active: bool
    registered_at: Optional[str]


class DeviceListResponse(BaseModel):
    """Admin device list with summary."""
    total: int
    online: int
    offline: int
    uptime_rate: float
    devices: list[DeviceResponse]
