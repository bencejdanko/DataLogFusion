"""
Replays sample.csv into the DataLogFusion backend at ~100 Hz.
Populates sensor:stream and sensor:latest in Redis so the frontend
dashboard shows real telemetry.

Usage:
    python sample-data/replay.py              # replay once at real speed
    python sample-data/replay.py --fast       # 10x speed (100ms → 10ms)
    python sample-data/replay.py --loop       # loop continuously
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import httpx

API_BASE   = "http://localhost:8000"
VEHICLE_ID = "V-001"
CSV_FILE   = Path(__file__).parent / "sample.csv"

COLUMNS = [
    "timestamp",
    "acc_x_mg", "acc_y_mg", "acc_z_mg",
    "gyr_x_mdps", "gyr_y_mdps", "gyr_z_mdps",
    "mag_x_mgauss", "mag_y_mgauss", "mag_z_mgauss",
    "press_hpa",
    "roll_deg", "pitch_deg", "yaw_deg",
]

INT_COLS   = {"acc_x_mg","acc_y_mg","acc_z_mg","gyr_x_mdps","gyr_y_mdps","gyr_z_mdps","mag_x_mgauss","mag_y_mgauss","mag_z_mgauss"}
FLOAT_COLS = {"press_hpa","roll_deg","pitch_deg","yaw_deg"}


def parse_row(row: list[str]) -> dict:
    payload = {}
    for col, val in zip(COLUMNS[1:], row[1:]):   # skip timestamp col
        if col in INT_COLS:
            payload[col] = int(val)
        elif col in FLOAT_COLS:
            payload[col] = float(val)
    return payload


def replay(fast: bool = False, loop: bool = False) -> None:
    rows = []
    with open(CSV_FILE, newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 14:
                rows.append(parse_row(row))

    delay = 0.001 if fast else 0.01   # 1ms (fast) or 10ms (~100 Hz)

    print(f"[replay] {len(rows)} rows → POST /telemetry/{VEHICLE_ID}  (delay={delay*1000:.0f}ms)")
    print(f"[replay] Dashboard: http://localhost:5173\n")

    iteration = 0
    with httpx.Client(base_url=API_BASE, timeout=5) as client:
        while True:
            iteration += 1
            for i, payload in enumerate(rows):
                resp = client.post(f"/telemetry/{VEHICLE_ID}", json=payload)
                if resp.status_code != 200:
                    print(f"[replay] POST failed: {resp.status_code}", file=sys.stderr)
                if (i + 1) % 100 == 0:
                    roll = payload.get("roll_deg", 0)
                    print(f"[replay] pass {iteration}  row {i+1}/{len(rows)}  roll={roll:.1f}°")
                time.sleep(delay)

            print(f"[replay] pass {iteration} complete ({len(rows)} rows)")
            if not loop:
                break

    print("[replay] done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="10× speed replay")
    parser.add_argument("--loop", action="store_true", help="loop continuously")
    args = parser.parse_args()
    replay(fast=args.fast, loop=args.loop)
