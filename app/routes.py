from flask import Blueprint, render_template, redirect, url_for
import subprocess
import os

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
    
def start_mediamtx():
    global mediamtx_process
    if mediamtx_process is None:
        mediamtx_process = subprocess.Popen([
            os.path.join(BASE_DIR, "../mediamtx/mediamtx"),
            os.path.join(BASE_DIR, "../mediamtx/custom_mediamtx.yml")
        ])

def stop_mediamtx():
    global mediamtx_process
    if mediamtx_process:
        mediamtx_process.terminate()
        mediamtx_process = None

@bp.route("/")
def index():
    global video_enabled, audio_enabled

    # Decide which stream to show
    if video_enabled and audio_enabled:
        stream_path = "cam_with_audio"
    elif video_enabled:
        stream_path = "cam"
    elif audio_enabled:
        stream_path = "mic"  # if you expose mic via MediaMTX
    else:
        stream_path = None
        stop_mediamtx()

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
    if video_enabled or audio_enabled:
        start_mediamtx()
    return redirect(url_for("main.index"))

@bp.route("/toggle_audio")
def toggle_audio():
    global audio_enabled
    audio_enabled = not audio_enabled
    if video_enabled or audio_enabled:
        start_mediamtx()
    return redirect(url_for("main.index"))

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