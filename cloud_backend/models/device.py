"""Device model for IoT device management."""
from __future__ import annotations

from sqlalchemy import Column, BigInteger, String, Float, Boolean, DateTime, func
from .base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False)
    device_mac = Column(String(17), unique=True, nullable=True)
    classroom_name = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_type = Column(String(20), nullable=False, default="real")
    device_status = Column(String(20), nullable=False, default="offline")
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    cpu_percent = Column(Float, nullable=True)
    mem_percent = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    capture_count = Column(BigInteger, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    registered_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
