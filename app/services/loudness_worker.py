# app/loudness_worker.py
import threading
import time
import numpy as np
import sounddevice as sd
from collections import deque

# Public state (read-only by callers)
Loudness = {
    'db': -120.0,
    'rms': 0.0,
    'history': deque(maxlen=120)  # keep last 120 samples
}

# Internal control objects
_worker_thread = None
_stop_event = threading.Event()
_lock = threading.Lock()

def measure_block(duration=0.5, samplerate=16000, device=None):
    """Record a short block and return (rms, db). Blocking for 'duration' seconds."""
    try:
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate,
                       channels=1, dtype='float32', device=device)
        sd.wait()
        audio = np.squeeze(audio)
        rms = float(np.sqrt(np.mean(audio ** 2) + 1e-16))
        db = 20 * np.log10(rms) if rms > 0 else -120.0
        return rms, db
    except Exception as e:
        print("measure_block error:", e)
        return 0.0, -120.0

def _loop(sample_interval=1.0, duration=0.5, samplerate=16000, device=None, stop_event=None):
    if stop_event is None:
        stop_event = _stop_event
    while not stop_event.is_set():
        rms, db = measure_block(duration=duration, samplerate=samplerate, device=device)
        with _lock:
            Loudness['rms'] = rms
            Loudness['db'] = round(db, 1)
            Loudness['history'].append({'ts': int(time.time()), 'db': Loudness['db']})
        # wait up to (sample_interval - duration), but wake early if stop_event set
        wait_time = max(0.0, sample_interval - duration)
        if stop_event.wait(wait_time):
            break

def start_loudness_worker(device=None, sample_interval=1.0, duration=0.5, samplerate=16000):
    """Start worker if not already running."""
    global _worker_thread, _stop_event
    if _worker_thread and _worker_thread.is_alive():
        return
    _stop_event.clear()
    _worker_thread = threading.Thread(
        target=_loop,
        kwargs={
            'device': device,
            'sample_interval': sample_interval,
            'duration': duration,
            'samplerate': samplerate,
            'stop_event': _stop_event
        },
        daemon=True
    )
    _worker_thread.start()

def stop_loudness_worker(timeout=None):
    """
    Signal worker to stop.
    If timeout is provided, join the thread for up to timeout seconds (can be 0).
    Returns True if thread stopped (or wasn't running), False if still alive after join timeout.
    """
    global _worker_thread, _stop_event
    _stop_event.set()
    if _worker_thread:
        _worker_thread.join(timeout)
        return not _worker_thread.is_alive()
    return True

def is_loudness_running():
    return _worker_thread is not None and _worker_thread.is_alive()
