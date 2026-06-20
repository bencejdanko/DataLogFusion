from detector import run as watch
from dtmf_tx import transmit

EVENT_NAMES = {
    '1': 'ROLLOVER',
    '2': 'HARD IMPACT',
    '3': 'SUSTAINED TILT',
    '4': 'SPIN-OUT',
    '5': 'AIRBORNE',
    '6': 'POST-CRASH STILLNESS',
}


def on_event(event_type: str) -> None:
    print(f"[ALERT] {EVENT_NAMES[event_type]} detected → transmitting *{event_type}#")
    transmit(event_type)


if __name__ == "__main__":
    print("Vehicle detector running. Watching Redis stream...")
    watch(on_event)
