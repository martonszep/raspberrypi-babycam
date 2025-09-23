import os
import subprocess
import time
import threading
from .system_metrics import get_ram_usage
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MediaState:
    _lock = threading.Lock()  # thread-safe singleton

    def __new__(cls):
        with cls._lock:
            if not hasattr(cls, "instance"):
                cls.instance = super(MediaState, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.video_enabled = False
        self.audio_enabled = False
        self.mediamtx_process = None

    def stop_mediamtx(self):
        if self.mediamtx_process:
            self.mediamtx_process.terminate()
            self.mediamtx_process.wait()
            self.mediamtx_process = None

    def restart_mediamtx(self, path: str):
        """Stop MediaMTX and start a new one with the given path."""
        self.stop_mediamtx()
        self.mediamtx_process = subprocess.Popen([
            os.path.join(BASE_DIR, "../mediamtx/mediamtx"),
            os.path.join(BASE_DIR, f"../mediamtx/mediamtx_{path}.yml")
        ])
        time.sleep(0.5)  # give it a moment to start

    def check_ram_and_restart(self, threshold_percent=90, path=None):
        """Optional: check RAM usage and restart MediaMTX if above threshold."""
        ram_percent = get_ram_usage()["percent"]
        if ram_percent > threshold_percent and path:
            logging.warning(
                "RAM usage %s%% > %s%%, restarting MediaMTX",
                ram_percent,
                threshold_percent,
            )
            self.restart_mediamtx(path)