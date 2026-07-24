#!/usr/bin/env python3
"""Simulate virtual device heartbeats for multi-classroom demo.

Sends heartbeat data for 3 virtual Pi nodes (Pi-02/03/04) every 30 seconds.
Pi-05 is intentionally NOT simulated — it stays offline to demonstrate
the cloud platform's automatic device-offline detection.

Usage: python scripts/simulate_virtual_devices.py
       (Run in background on the same PC as FastAPI)
"""

import json
import random
import time
from datetime import datetime, timezone

import requests

CLOUD_URL = "http://localhost:8011/api/device/heartbeat"

VIRTUAL_DEVICES = [
    {
        "device_mac": "b8:27:eb:00:00:02",
        "device_name": "Pi-02",
        "classroom_name": "302教室",
        "device_type": "virtual",
        "cpu_range": (18.0, 38.0),
        "mem_range": (28.0, 52.0),
        "disk_range": (22.0, 42.0),
        "temp_range": (40.0, 50.0),
    },
    {
        "device_mac": "b8:27:eb:00:00:03",
        "device_name": "Pi-03",
        "classroom_name": "303教室",
        "device_type": "virtual",
        "cpu_range": (30.0, 55.0),
        "mem_range": (35.0, 58.0),
        "disk_range": (30.0, 50.0),
        "temp_range": (43.0, 53.0),
    },
    {
        "device_mac": "b8:27:eb:00:00:04",
        "device_name": "Pi-04",
        "classroom_name": "304教室",
        "device_type": "virtual",
        "cpu_range": (15.0, 30.0),
        "mem_range": (25.0, 45.0),
        "disk_range": (18.0, 35.0),
        "temp_range": (38.0, 45.0),
    },
    # Pi-05 (MAC: b8:27:eb:00:00:05) is intentionally NOT in this list.
    # It will be pre-registered in the DB via data seed but receives no
    # heartbeat → auto-marked offline by the cloud timeout checker.
]


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] "
          f"Virtual device simulator started: {len(VIRTUAL_DEVICES)} nodes")
    print(f"  Target: {CLOUD_URL}")
    print(f"  Interval: 30s")
    print(f"  Simulating: {', '.join(d['device_name'] for d in VIRTUAL_DEVICES)}")
    print(f"  NOT simulating Pi-05 → stays offline (demo fault detection)")

    while True:
        for dev in VIRTUAL_DEVICES:
            payload = {
                "device_mac": dev["device_mac"],
                "device_name": dev["device_name"],
                "classroom_name": dev["classroom_name"],
                "device_type": dev["device_type"],
                "cpu_percent": round(random.uniform(*dev["cpu_range"]), 1),
                "mem_percent": round(random.uniform(*dev["mem_range"]), 1),
                "disk_percent": round(random.uniform(*dev["disk_range"]), 1),
                "temperature": round(random.uniform(*dev["temp_range"]), 1),
                "timestamp": int(time.time()),
            }
            try:
                resp = requests.post(CLOUD_URL, json=payload, timeout=5)
                status = "✓" if resp.ok else f"✗ {resp.status_code}"
            except Exception as e:
                status = f"✗ {e}"

            print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                  f"{dev['device_name']} ({dev['classroom_name']}) "
                  f"CPU={payload['cpu_percent']}% {status}")

        time.sleep(30)


if __name__ == "__main__":
    main()
