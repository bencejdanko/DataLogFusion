"""
Command post entry point.
Starts the fetch.ai agent bureau in a background thread, then blocks on DTMF mic input.
"""
import threading
import time

from agents import bureau, dispatch
from dtmf_rx import listen


def on_dtmf(event_type: str) -> None:
    print(f"[RX] DTMF decoded → event_type={event_type}")
    dispatch(event_type)   # puts into queue, picked up by MonitorAgent on next poll


if __name__ == "__main__":
    threading.Thread(target=bureau.run, daemon=True).start()
    time.sleep(2)          # let agents register before mic input starts
    print("[RX] Command post ready. Agents running.")
    listen(on_dtmf)        # blocks forever on mic input
