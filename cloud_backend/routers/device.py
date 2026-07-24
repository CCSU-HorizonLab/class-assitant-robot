"""Device heartbeat and management API routes."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, HTTPException, status

from ..config import settings
from ..schemas.device import HeartbeatRequest, DeviceListResponse, DeviceResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Device API"])


# ── Database helpers (mirror auth.py pattern) ──────────────────────────

def _database_url() -> str:
    database_url = settings.database_url.strip()
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL database URL is required",
        )
    return database_url


def _connect():
    return psycopg2.connect(_database_url())


def _ensure_devices_table():
    """Idempotent schema migration for the devices table."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id              BIGSERIAL PRIMARY KEY,
                    device_name     VARCHAR(100) NOT NULL,
                    device_mac      VARCHAR(17) UNIQUE,
                    classroom_name  VARCHAR(100),
                    ip_address      VARCHAR(45),
                    device_type     VARCHAR(20) NOT NULL DEFAULT 'real',
                    device_status   VARCHAR(20) NOT NULL DEFAULT 'offline',
                    last_heartbeat  TIMESTAMPTZ,
                    cpu_percent     REAL DEFAULT 0,
                    mem_percent     REAL DEFAULT 0,
                    disk_percent    REAL DEFAULT 0,
                    temperature     REAL,
                    capture_count   BIGINT NOT NULL DEFAULT 0,
                    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
                    registered_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.commit()


def _seed_demo_devices():
    """Pre-register demo devices (including offline Pi-05) if table is empty."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM devices")
            count = cur.fetchone()[0]
            if count > 0:
                return  # Already has data, skip seeding

            demo_devices = [
                ("Pi-01", "b8:27:eb:00:00:01", "301教室", "real"),
                ("Pi-02", "b8:27:eb:00:00:02", "302教室", "virtual"),
                ("Pi-03", "b8:27:eb:00:00:03", "303教室", "virtual"),
                ("Pi-04", "b8:27:eb:00:00:04", "304教室", "virtual"),
                ("Pi-05", "b8:27:eb:00:00:05", "305教室", "virtual"),
            ]
            now = datetime.now(timezone.utc)
            for name, mac, classroom, dtype in demo_devices:
                # Pi-05 starts as offline with no heartbeat; others start offline too
                # until their first heartbeat arrives
                cur.execute(
                    """
                    INSERT INTO devices
                        (device_name, device_mac, classroom_name, device_type,
                         device_status, registered_at, updated_at)
                    VALUES (%s, %s, %s, %s, 'offline', %s, %s)
                    ON CONFLICT (device_mac) DO NOTHING
                    """,
                    (name, mac, classroom, dtype, now, now),
                )
            conn.commit()
            logger.info("Seeded %d demo devices (Pi-01 real + Pi-02~05 virtual)", len(demo_devices))


# ── Heartbeat endpoint ─────────────────────────────────────────────────

@router.post("/device/heartbeat")
async def device_heartbeat(payload: HeartbeatRequest):
    """Receive heartbeat from a device (real Pi or virtual simulator).

    If the device is not yet registered, auto-register it.
    Updates CPU / memory / disk / temperature / heartbeat timestamp.
    Always sets status to 'online' on successful heartbeat.
    """
    try:
        _ensure_devices_table()
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Check if device exists
                cur.execute(
                    "SELECT id, device_status FROM devices WHERE device_mac = %s",
                    (payload.device_mac,),
                )
                existing = cur.fetchone()

                if existing:
                    cur.execute(
                        """
                        UPDATE devices
                        SET device_status   = 'online',
                            last_heartbeat  = %s,
                            cpu_percent     = %s,
                            mem_percent     = %s,
                            disk_percent    = %s,
                            temperature     = %s,
                            ip_address      = COALESCE(%s, ip_address),
                            updated_at      = NOW()
                        WHERE device_mac = %s
                        """,
                        (
                            datetime.now(timezone.utc),
                            payload.cpu_percent,
                            payload.mem_percent,
                            payload.disk_percent,
                            payload.temperature,
                            None,  # ip_address not in heartbeat for now
                            payload.device_mac,
                        ),
                    )
                else:
                    # Auto-register new device
                    cur.execute(
                        """
                        INSERT INTO devices
                            (device_name, device_mac, classroom_name, device_type,
                             device_status, last_heartbeat,
                             cpu_percent, mem_percent, disk_percent, temperature)
                        VALUES (%s, %s, %s, %s, 'online', %s, %s, %s, %s, %s)
                        """,
                        (
                            payload.device_name or f"Device-{payload.device_mac[-4:]}",
                            payload.device_mac,
                            payload.classroom_name,
                            payload.device_type or "real",
                            datetime.now(timezone.utc),
                            payload.cpu_percent,
                            payload.mem_percent,
                            payload.disk_percent,
                            payload.temperature,
                        ),
                    )
                conn.commit()

        return {"success": True, "message": "heartbeat received"}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Heartbeat error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Heartbeat processing failed: {exc}")


# ── Admin query endpoints ──────────────────────────────────────────────

def _row_to_response(row: Dict[str, Any]) -> DeviceResponse:
    return DeviceResponse(
        id=row["id"],
        device_name=row["device_name"],
        device_mac=row.get("device_mac"),
        classroom_name=row.get("classroom_name"),
        device_type=row.get("device_type", "real"),
        device_status=row.get("device_status", "offline"),
        last_heartbeat=row["last_heartbeat"].isoformat() if row.get("last_heartbeat") else None,
        cpu_percent=row.get("cpu_percent"),
        mem_percent=row.get("mem_percent"),
        disk_percent=row.get("disk_percent"),
        temperature=row.get("temperature"),
        capture_count=row.get("capture_count", 0),
        is_active=row.get("is_active", True),
        registered_at=row["registered_at"].isoformat() if row.get("registered_at") else None,
    )


@router.get("/admin/devices", response_model=DeviceListResponse)
async def list_devices():
    """Return all registered devices with a summary."""
    try:
        _ensure_devices_table()
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM devices
                    WHERE is_active = TRUE
                    ORDER BY device_name ASC
                """)
                rows = cur.fetchall()

        devices = [_row_to_response(row) for row in rows]
        total = len(devices)
        online = sum(1 for d in devices if d.device_status == "online")
        offline = total - online
        uptime_rate = round(online / total * 100, 1) if total > 0 else 0.0

        return DeviceListResponse(
            total=total,
            online=online,
            offline=offline,
            uptime_rate=uptime_rate,
            devices=devices,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("List devices error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {exc}")


# ── Background task: heartbeat timeout auto-offline ────────────────────

_heartbeat_task: Optional[asyncio.Task] = None


async def _heartbeat_timeout_checker(interval: int = 30, timeout_seconds: int = 90):
    """Background task: scan devices every `interval` seconds.

    Any device whose last_heartbeat is older than `timeout_seconds`
    is automatically marked as 'offline'.
    """
    while True:
        await asyncio.sleep(interval)
        try:
            with _connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE devices
                        SET device_status = 'offline',
                            updated_at = NOW()
                        WHERE device_status = 'online'
                          AND last_heartbeat IS NOT NULL
                          AND last_heartbeat < NOW() - make_interval(secs => %s)
                        """,
                        (timeout_seconds,),
                    )
                    updated = cur.rowcount
                    if updated:
                        conn.commit()
                        logger.info("Auto-offline: %s device(s) marked offline", updated)
                    else:
                        conn.rollback()
        except Exception as exc:
            logger.warning("Heartbeat timeout checker error: %s", exc)


def start_heartbeat_checker():
    """Start the background heartbeat timeout checker. Call from lifespan."""
    global _heartbeat_task
    if _heartbeat_task is not None:
        return
    _ensure_devices_table()
    _seed_demo_devices()
    _heartbeat_task = asyncio.create_task(_heartbeat_timeout_checker())
    logger.info("Heartbeat timeout checker started (interval=30s, timeout=90s)")


async def stop_heartbeat_checker():
    """Stop the background heartbeat timeout checker. Call from lifespan shutdown."""
    global _heartbeat_task
    if _heartbeat_task is not None:
        _heartbeat_task.cancel()
        try:
            await _heartbeat_task
        except asyncio.CancelledError:
            pass
        _heartbeat_task = None
        logger.info("Heartbeat timeout checker stopped")
