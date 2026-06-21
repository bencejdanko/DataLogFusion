"""
End-to-end pipeline test without radio hardware.

1. Replays sample.csv → backend (populates Redis/telemetry)
2. Fetches /history to get telemetry context
3. Calls Claude Haiku with a simulated event
4. POSTs the generated report to /incidents

Run this to validate the full software stack before connecting radios.

Usage:
    cd DataLogFusion
    ANTHROPIC_API_KEY=sk-... python sample-data/simulate_incident.py
    ANTHROPIC_API_KEY=sk-... python sample-data/simulate_incident.py --event 2
"""

import argparse
import csv
import math
import os
import sys
import time
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE   = "http://localhost:8000"
VEHICLE_ID = "V-001"
CSV_FILE   = Path(__file__).parent / "sample.csv"

EVENT_NAMES = {
    '1': 'Vehicle Rollover',
    '2': 'Hard Impact / Collision',
    '3': 'Dangerous Sustained Tilt',
    '4': 'Spin-Out / Loss of Control',
    '5': 'Vehicle Airborne',
    '6': 'Post-Crash Stillness',
}

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
    for col, val in zip(COLUMNS[1:], row[1:]):
        if col in INT_COLS:
            payload[col] = int(val)
        elif col in FLOAT_COLS:
            payload[col] = float(val)
    return payload


# ── Step 1: Replay CSV → backend ─────────────────────────────────────────────

def replay_csv(client: httpx.Client) -> list[dict]:
    rows = []
    with open(CSV_FILE, newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 14:
                rows.append(parse_row(row))

    print(f"\n[1/4] Feeding {len(rows)} rows → /telemetry/{VEHICLE_ID} (fast mode) ...")
    for i, payload in enumerate(rows):
        resp = client.post(f"/telemetry/{VEHICLE_ID}", json=payload)
        if resp.status_code != 200:
            print(f"  POST failed row {i}: {resp.status_code}", file=sys.stderr)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(rows)} rows ingested")
        time.sleep(0.001)   # 1ms → ~1000 rows/s

    print(f"  done. {len(rows)} rows ingested.\n")
    return rows


# ── Step 2: Fetch telemetry context from /history ────────────────────────────

def fetch_history(client: httpx.Client, count: int = 100) -> list[dict]:
    print(f"[2/4] Fetching last {count} readings from /history ...")
    resp = client.get("/history", params={"count": count})
    data = resp.json()
    print(f"  received {len(data)} readings\n")
    return data


# ── Step 3: Summarise for Claude ─────────────────────────────────────────────

def summarise(readings: list[dict]) -> str:
    if not readings:
        return "No telemetry available."
    rolls   = [float(r.get('roll_deg',  0)) for r in readings if 'roll_deg'  in r]
    pitches = [float(r.get('pitch_deg', 0)) for r in readings if 'pitch_deg' in r]
    mags = [
        math.sqrt(float(r.get('acc_x_mg',0))**2
                + float(r.get('acc_y_mg',0))**2
                + float(r.get('acc_z_mg',0))**2) / 1000
        for r in readings if 'acc_x_mg' in r
    ]
    return (
        f"Readings: {len(readings)} samples (~{len(readings)/100:.1f}s window)\n"
        f"Roll  — peak: {max(abs(v) for v in rolls):.1f}°  "
        f"current: {rolls[0] if rolls else 0:.1f}°\n"
        f"Pitch — peak: {max(abs(v) for v in pitches):.1f}°  "
        f"current: {pitches[0] if pitches else 0:.1f}°\n"
        f"Accel — peak: {max(mags):.2f}g  avg: {sum(mags)/max(len(mags),1):.2f}g"
    )


# ── Step 4: Call Claude → POST /incidents ────────────────────────────────────

def generate_and_post(client: httpx.Client, event_type: str, history: list[dict]) -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[3/4] ERROR: ANTHROPIC_API_KEY not set. Export it and re-run.", file=sys.stderr)
        sys.exit(1)

    event_name = EVENT_NAMES[event_type]
    summary    = summarise(history)

    print(f"[3/4] Calling Claude Haiku → incident report for '{event_name}' ...")
    print(f"  telemetry summary:\n{summary}\n")

    claude = anthropic.Anthropic(api_key=api_key)
    prompt = f"""You are an incident analytics agent for a rural first-responder vehicle safety system.

Event detected: {event_name}

Sensor telemetry from the period before the event:
{summary}

Generate a structured incident report with exactly these four sections:

## What Happened
(2-3 sentences, plain language, data-driven)

## Contributing Factors
(3-5 bullet points based on the sensor readings)

## Severity Assessment
State: LOW / MEDIUM / HIGH — then one sentence justifying the rating.

## Recommended Immediate Actions
(numbered list, 3-5 actions for first responders on scene)"""

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    report = response.content[0].text

    print(f"\n{'='*60}")
    print(f"INCIDENT REPORT — {event_name.upper()}")
    print('='*60)
    print(report)
    print('='*60)

    print(f"\n[4/4] Posting report to /incidents ...")
    resp = client.post("/incidents", json={
        "event_type": event_type,
        "event_name": event_name,
        "report":     report,
        "telemetry_window": history[:20],
    })
    result = resp.json()
    print(f"  response: {result}")
    print(f"\n  Dashboard: http://localhost:5173  (incident card should appear within 3s)")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end pipeline test using sample CSV data")
    parser.add_argument("--event", default="1", choices=list(EVENT_NAMES.keys()),
                        help="Event type to simulate (default: 1 = Vehicle Rollover)")
    args = parser.parse_args()

    print("DataLogFusion — End-to-End Pipeline Test")
    print(f"Event: {args.event} — {EVENT_NAMES[args.event]}\n")

    with httpx.Client(base_url=API_BASE, timeout=10) as client:
        # Health check
        try:
            h = client.get("/health")
            print(f"[0/4] Backend health: {h.json()}\n")
        except Exception as e:
            print(f"[0/4] ERROR: Cannot reach backend at {API_BASE} — {e}", file=sys.stderr)
            print("       Run:  cd backend && python main.py", file=sys.stderr)
            sys.exit(1)

        replay_csv(client)
        history = fetch_history(client, count=100)
        generate_and_post(client, args.event, history)


if __name__ == "__main__":
    main()
