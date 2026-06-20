import os
import subprocess
import tempfile
import wave
import numpy as np

SAMPLE_RATE = 44100
TONE_MS = 250
GAP_MS  = 70

DTMF_FREQS = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
    '*': (941, 1209), '#': (941, 1477),
}


def _tone(digit: str) -> np.ndarray:
    f1, f2 = DTMF_FREQS[digit]
    n = int(SAMPLE_RATE * TONE_MS / 1000)
    t = np.arange(n) / SAMPLE_RATE
    samples = 0.5 * (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t))
    return (samples * 32767).astype(np.int16)


def _silence() -> np.ndarray:
    return np.zeros(int(SAMPLE_RATE * GAP_MS / 1000), dtype=np.int16)


def transmit(event_digit: str) -> None:
    """Play *E# sequence over system audio. event_digit: '1'..'6'"""
    audio = np.concatenate([s for d in ['*', event_digit, '#']
                             for s in (_tone(d), _silence())])
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        fname = f.name
    with wave.open(fname, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    try:
        # aplay for Linux/QNX; fallback to ffplay if not found
        try:
            subprocess.run(['aplay', '-q', fname], check=True)
        except FileNotFoundError:
            subprocess.run(
                ['ffplay', '-f', 's16le', '-ar', '44100', '-ac', '1',
                 '-nodisp', '-autoexit', fname],
                check=True,
            )
    finally:
        os.unlink(fname)
