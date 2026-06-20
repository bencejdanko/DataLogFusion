"""
fetch.ai multi-agent incident analytics.

MonitorAgent: polls for incoming events, fetches telemetry context, forwards to AnalystAgent.
AnalystAgent: calls Claude, generates structured 4-section report, POSTs to /incidents.

External code calls dispatch(event_type) to trigger the pipeline.
"""
import math
import os
import queue as _queue

import anthropic
import httpx
from dotenv import load_dotenv
from uagents import Agent, Bureau, Context, Model

load_dotenv()

API_BASE      = os.getenv("API_BASE", "http://localhost:8000")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
_claude       = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

EVENT_NAMES = {
    '1': 'Vehicle Rollover',
    '2': 'Hard Impact / Collision',
    '3': 'Dangerous Sustained Tilt',
    '4': 'Spin-Out / Loss of Control',
    '5': 'Vehicle Airborne',
    '6': 'Post-Crash Stillness',
}

# Thread-safe bridge: DTMF decoder (sync) → Monitor Agent (async)
_event_queue: _queue.Queue = _queue.Queue()


def dispatch(event_type: str) -> None:
    """Call from sync code (DTMF decoder) to inject an event into the agent pipeline."""
    _event_queue.put(event_type)


# ── Message models ─────────────────────────────────────────────────────────────

class EnrichedEvent(Model):
    event_type: str
    event_name: str
    telemetry_summary: str
    telemetry_window: list


# ── Agents ─────────────────────────────────────────────────────────────────────

monitor = Agent(name="monitor_agent", seed="monitor_agent_seed_v1", port=8101)
analyst = Agent(name="analyst_agent", seed="analyst_agent_seed_v1", port=8102)


def _fetch_telemetry(count: int = 100) -> list[dict]:
    try:
        resp = httpx.get(f"{API_BASE}/history", params={"count": count}, timeout=5)
        return resp.json()
    except Exception as e:
        print(f"[monitor] telemetry fetch failed: {e}")
        return []


def _summarise(readings: list[dict]) -> str:
    if not readings:
        return "No telemetry available."
    rolls   = [float(r.get('roll_deg', 0))  for r in readings if 'roll_deg'  in r]
    pitches = [float(r.get('pitch_deg', 0)) for r in readings if 'pitch_deg' in r]
    mags    = [
        math.sqrt(float(r.get('acc_x_mg', 0)) ** 2
                + float(r.get('acc_y_mg', 0)) ** 2
                + float(r.get('acc_z_mg', 0)) ** 2) / 1000
        for r in readings if 'acc_x_mg' in r
    ]
    return (
        f"Readings: {len(readings)} samples (~{len(readings) / 100:.1f}s window)\n"
        f"Roll  — peak: {max((abs(v) for v in rolls), default=0):.1f}°\n"
        f"Pitch — peak: {max((abs(v) for v in pitches), default=0):.1f}°\n"
        f"Accel — peak: {max(mags, default=0):.2f}g  "
        f"avg: {sum(mags) / max(len(mags), 1):.2f}g"
    )


@monitor.on_interval(period=0.5)
async def check_for_events(ctx: Context) -> None:
    """Poll the thread-safe queue for events injected by the DTMF decoder."""
    try:
        event_type = _event_queue.get_nowait()
    except _queue.Empty:
        return

    ctx.logger.info(f"[monitor] processing event_type={event_type}")
    readings = _fetch_telemetry(100)
    enriched = EnrichedEvent(
        event_type=event_type,
        event_name=EVENT_NAMES.get(event_type, 'Unknown Event'),
        telemetry_summary=_summarise(readings),
        telemetry_window=readings[:20],
    )
    await ctx.send(analyst.address, enriched)


@analyst.on_message(model=EnrichedEvent)
async def handle_enriched_event(ctx: Context, sender: str, msg: EnrichedEvent) -> None:
    ctx.logger.info(f"[analyst] generating report for {msg.event_name}")

    prompt = f"""You are an incident analytics agent for a rural first-responder vehicle safety system.

Event detected: {msg.event_name}

Sensor telemetry from the period before the event:
{msg.telemetry_summary}

Generate a structured incident report with exactly these four sections:

## What Happened
(2-3 sentences, plain language, data-driven)

## Contributing Factors
(3-5 bullet points based on the sensor readings)

## Severity Assessment
State: LOW / MEDIUM / HIGH — then one sentence justifying the rating.

## Recommended Immediate Actions
(numbered list, 3-5 actions for first responders on scene)"""

    response = _claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    report = response.content[0].text
    ctx.logger.info("[analyst] report generated")
    print(f"\n{'=' * 60}\n{msg.event_name.upper()}\n{'=' * 60}\n{report}\n{'=' * 60}\n")

    try:
        httpx.post(
            f"{API_BASE}/incidents",
            json={
                "event_type": msg.event_type,
                "event_name": msg.event_name,
                "report": report,
                "telemetry_window": msg.telemetry_window,
            },
            timeout=5,
        )
        ctx.logger.info("[analyst] incident posted to dashboard")
    except Exception as e:
        ctx.logger.warning(f"[analyst] dashboard post failed: {e}")


# ── Bureau ──────────────────────────────────────────────────────────────────────

bureau = Bureau(port=8100)
bureau.add(monitor)
bureau.add(analyst)
