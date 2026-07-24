#!/usr/bin/env python3
"""Device heartbeat reporter for Raspberry Pi.

Reports system status (CPU, memory, disk, temperature) to the cloud backend
every 30 seconds. Uses MQTT as primary channel with automatic HTTP fallback.

Usage:  python device_heartbeat.py
        (Run via systemd or supervisor for persistence)
"""

import json
import os
import socket
import time
import uuid
from datetime import datetime, timezone

import psutil
import requests

# ── Configuration ───────────────────────────────────────────────────────

CLOUD_HOST = os.environ.get("CLOUD_HOST", "192.168.31.22")
CLOUD_PORT = int(os.environ.get("CLOUD_PORT", "8011"))
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", CLOUD_HOST)
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "30"))

HTTP_HEARTBEAT_URL = f"http://{CLOUD_HOST}:{CLOUD_PORT}/api/device/heartbeat"
MQTT_TOPIC = "classroom/device/heartbeat"

# ── Device identity ─────────────────────────────────────────────────────


def _get_mac():
    """Get the MAC address of the primary network interface."""
    mac = uuid.getnode()
    return ":".join([f"{(mac >> ele) & 0xff:02x}" for ele in range(0, 8 * 6, 8)][::-1])


DEVICE_MAC = _get_mac()
DEVICE_NAME = os.environ.get("DEVICE_NAME", "Pi-01")
CLASSROOM_NAME = os.environ.get("CLASSROOM_NAME", "301教室")


# ── System info ─────────────────────────────────────────────────────────


def _read_cpu_temp():
    """Read Raspberry Pi CPU temperature."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(float(f.read().strip()) / 1000.0, 1)
    except Exception:
        return None


def collect_system_info() -> dict:
    return {
        "device_mac": DEVICE_MAC,
        "device_name": DEVICE_NAME,
        "classroom_name": CLASSROOM_NAME,
        "device_type": "real",
        "cpu_percent": round(psutil.cpu_percent(interval=1), 1),
        "mem_percent": round(psutil.virtual_memory().percent, 1),
        "disk_percent": round(psutil.disk_usage("/").percent, 1),
        "temperature": _read_cpu_temp(),
        "timestamp": int(time.time()),
    }


# ── Transport ───────────────────────────────────────────────────────────


def send_via_mqtt(payload: dict):
    """Primary: publish heartbeat via MQTT."""
    import paho.mqtt.client as mqtt

    client = mqtt.Client(client_id=f"pi-heartbeat-{DEVICE_MAC.replace(':', '')}")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    client.disconnect()


def send_via_http(payload: dict):
    """Fallback: POST heartbeat via HTTP."""
    resp = requests.post(HTTP_HEARTBEAT_URL, json=payload, timeout=5)
    resp.raise_for_status()


# ── Main loop ───────────────────────────────────────────────────────────


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] "
          f"Heartbeat reporter started: {DEVICE_NAME} ({DEVICE_MAC}) "
          f"→ cloud {CLOUD_HOST}:{CLOUD_PORT}")
    print(f"  MQTT broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    print(f"  HTTP fallback: {HTTP_HEARTBEAT_URL}")
    print(f"  Interval: {HEARTBEAT_INTERVAL}s")

    consecutive_mqtt_failures = 0

    while True:
        payload = collect_system_info()

        # Try MQTT first
        try:
            send_via_mqtt(payload)
            consecutive_mqtt_failures = 0
            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                  f"MQTT ✓ CPU={payload['cpu_percent']}% "
                  f"MEM={payload['mem_percent']}% TEMP={payload['temperature']}")
        except Exception as e:
            consecutive_mqtt_failures += 1
            # Fallback to HTTP
            try:
                send_via_http(payload)
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                      f"HTTP ✓ (MQTT failed x{consecutive_mqtt_failures}: {e})")
            except Exception as e2:
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                      f"✗ Both MQTT and HTTP failed: {e2}")

        time.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    main()
