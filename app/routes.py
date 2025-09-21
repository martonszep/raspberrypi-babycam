from flask import Blueprint, render_template, redirect, url_for, jsonify
import subprocess
import os
import time
from .services.loudness_worker import Loudness, start_loudness_worker, stop_loudness_worker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bp = Blueprint("main", __name__)

# Global variable to track stream process
video_enabled = False
audio_enabled = False
mediamtx_process = None

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return None
    
def start_mediamtx(path: str):
    global mediamtx_process
    if mediamtx_process is None:
        mediamtx_process = subprocess.Popen([
            os.path.join(BASE_DIR, "../mediamtx/mediamtx"),
            os.path.join(BASE_DIR, f"../mediamtx/mediamtx_{path}.yml")
        ])

def stop_mediamtx():
    global mediamtx_process
    if mediamtx_process:
        mediamtx_process.terminate()
        mediamtx_process.wait()
        mediamtx_process = None

def switch_mediamtx(path):
    """Stop MediaMTX and restart it to use a new path."""
    stop_mediamtx()
    start_mediamtx(path)
    time.sleep(0.5)  # Give it a moment to start


@bp.route("/")
def index():
    global video_enabled, audio_enabled

    # Decide which stream to show
    if video_enabled and audio_enabled:
        stream_path = "cam_with_audio"
        switch_mediamtx(stream_path)
    elif video_enabled:
        stream_path = "cam"
        switch_mediamtx(stream_path)
    elif audio_enabled:
        stream_path = "audio_only"
        switch_mediamtx(stream_path)
        # start_loudness_worker(device='hw:0,0', sample_interval=1.0, duration=0.5, samplerate=44100) 
    else:
        stream_path = None
        stop_mediamtx()
        # stop_loudness_worker()

    temp_c = get_cpu_temp()
    return render_template(
        "index.html",
        video_enabled=video_enabled,
        audio_enabled=audio_enabled,
        stream_path=stream_path,
        temp_c=temp_c,
    )

@bp.route("/toggle_video")
def toggle_video():
    global video_enabled
    video_enabled = not video_enabled
    return redirect(url_for("main.index"))

@bp.route("/toggle_audio")
def toggle_audio():
    global audio_enabled
    audio_enabled = not audio_enabled
    return redirect(url_for("main.index"))

@bp.route('/loudness')
def loudness():
    # returns latest db and short history
    h = list(Loudness['history'])
    return jsonify({
        'db': Loudness['db'],
        'rms': Loudness['rms'],
        'history': h
    })

@bp.route("/temperature")
def temperature():
    """Return current CPU temperature for AJAX refresh"""
    return str(get_cpu_temp())

@bp.route("/shutdown")
def shutdown():
    """Shutdown the Raspberry Pi"""
    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
    return "Shutting down..."

@bp.route("/reboot")
def reboot():
    """Reboot the Raspberry Pi"""
    subprocess.Popen(["sudo", "reboot"])
    return "Rebooting..."