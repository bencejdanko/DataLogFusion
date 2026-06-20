import numpy as np
import sounddevice as sd
from typing import Callable, Optional

SAMPLE_RATE = 44100
BLOCK_SIZE  = int(SAMPLE_RATE * 0.15)   # 150 ms analysis windows
THRESHOLD   = 3e5   # Goertzel power threshold — lower to 1e5 if tones drop over radio

ROW_FREQS = [697, 770, 852, 941]
COL_FREQS = [1209, 1336, 1477]
KEYPAD    = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['*', '0', '#']]


def _goertzel(samples: np.ndarray, freq: float) -> float:
    n = len(samples)
    coeff = 2.0 * np.cos(2.0 * np.pi * int(0.5 + n * freq / SAMPLE_RATE) / n)
    q1 = q2 = 0.0
    for s in samples:
        q0 = coeff * q1 - q2 + float(s)
        q2, q1 = q1, q0
    return q1 * q1 + q2 * q2 - q1 * q2 * coeff


def _detect(samples: np.ndarray) -> Optional[str]:
    rp = [_goertzel(samples, f) for f in ROW_FREQS]
    cp = [_goertzel(samples, f) for f in COL_FREQS]
    r = max(range(4), key=lambda i: rp[i])
    c = max(range(3), key=lambda i: cp[i])
    if rp[r] < THRESHOLD or cp[c] < THRESHOLD:
        return None
    return KEYPAD[r][c]


def listen(on_event: Callable[[str], None]) -> None:
    """
    Blocks forever on mic input.
    Calls on_event(event_type) when a complete *E# sequence is decoded.
    event_type: '1'..'6'
    """
    payload: list[str] = []
    in_seq = False
    prev: Optional[str] = None

    def callback(indata, frames, time_info, status):
        nonlocal in_seq, prev, payload
        digit = _detect(indata[:, 0])
        if digit == prev:
            return          # debounce: skip repeated reads of same sustained tone
        prev = digit
        if digit is None:
            return
        if digit == '*':
            payload, in_seq = [], True
            return
        if not in_seq:
            return
        if digit == '#':
            if len(payload) == 1:
                on_event(payload[0])
            payload, in_seq = [], False
            return
        payload.append(digit)

    print("[RX] Listening for DTMF *E# on mic input...")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                        blocksize=BLOCK_SIZE, callback=callback):
        while True:
            sd.sleep(500)
