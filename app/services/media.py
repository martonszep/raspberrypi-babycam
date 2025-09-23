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
        self.stream_path = None

    def stop_mediamtx(self):
        if self.mediamtx_process:
            self.mediamtx_process.terminate()
            self.mediamtx_process.wait()
            self.mediamtx_process = None

    def start_mediamtx(self, path):
        if path == self.stream_path and self.mediamtx_process:
            # Already running the correct path
            return
        self.stop_mediamtx()
        self.mediamtx_process = subprocess.Popen([
            os.path.join(BASE_DIR, "../mediamtx/mediamtx"),
            os.path.join(BASE_DIR, f"../mediamtx/mediamtx_{path}.yml")
        ])
        self.stream_path = path
        # time.sleep(0.5)  # Give it a moment to start

    def restart_mediamtx(self):
        if self.stream_path:
            self.start_mediamtx(self.stream_path)

    def check_ram_and_restart(self, threshold_percent=90):
        """Optional: check RAM usage and restart MediaMTX if above threshold."""
        ram_percent = get_ram_usage()["percent"]
        if ram_percent > threshold_percent:
            logging.warning(
                "RAM usage %s%% > %s%%, restarting MediaMTX",
                ram_percent,
                threshold_percent,
            )
            self.restart_mediamtx()

    def start_ram_monitor(self, path, interval=30, threshold_percent=90):
        """Start a background thread to periodically check RAM and restart MediaMTX if needed."""
        def monitor():
            while True:
                self.check_ram_and_restart(threshold_percent=threshold_percent)
                time.sleep(interval)

        t = threading.Thread(target=monitor, daemon=True)
        t.start()