from flask import Blueprint, render_template, redirect, url_for, jsonify
import subprocess
import os
import time
from .services.media import MediaState
from .services.system_metrics import get_cpu_temp, get_cpu_load, get_ram_usage, get_throttle_status
# from .services.loudness_worker import Loudness, start_loudness_worker, stop_loudness_worker

bp = Blueprint("main", __name__)
media_state = MediaState() # Singleton instance


@bp.route("/")
def index():
    global video_enabled, audio_enabled

    # Decide which stream to show
    if media_state.video_enabled and media_state.audio_enabled:
        path = "cam_with_audio"
    elif media_state.video_enabled:
        path = "cam"
        # stop_loudness_worker()
    elif media_state.audio_enabled:
        path = "audio_only"
        # start_loudness_worker(device='hw:0,0', sample_interval=1.0, duration=0.5, samplerate=44100) 
    else:
        path = None
        # stop_loudness_worker()

    if path:
        media_state.start_mediamtx(path)
    else:
        media_state.stop_mediamtx()

    throttle_status = get_throttle_status['active_issues']
    return render_template(
        "index.html",
        video_enabled=media_state.video_enabled,
        audio_enabled=media_state.audio_enabled,
        stream_path=path,
        cpu_temp = str(get_cpu_temp()),
        cpu_load = str(get_cpu_load()),
        ram = get_ram_usage(),
        throttle = "; ".join(throttle_status) if throttle_status else "No issues",
    )

@bp.route("/toggle_video")
def toggle_video():
    media_state.video_enabled = not media_state.video_enabled
    return redirect(url_for("main.index"))

@bp.route("/toggle_audio")
def toggle_audio():
    media_state.audio_enabled = not media_state.audio_enabled
    return redirect(url_for("main.index"))

# @bp.route('/loudness')
# def loudness():
#     # returns latest db and short history
#     h = list(Loudness['history'])
#     return jsonify({
#         'db': Loudness['db'],
#         'rms': Loudness['rms'],
#         'history': h
#     })

@bp.route("/metrics")
def metrics():
    """Return system metrics as JSON (for AJAX updates)."""
    return jsonify({
        "cpu_temp": get_cpu_temp(),
        "cpu_load": get_cpu_load(),
        "ram": get_ram_usage(),
        "throttle": get_throttle_status(),
    })

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