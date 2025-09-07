from flask import Blueprint, render_template, redirect, url_for, jsonify
import subprocess
import os
from .services.loudness_worker import Loudness, start_loudness_worker, stop_loudness_worker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bp = Blueprint("main", __name__)

# Global variable to track stream process
video_enabled = False
audio_enabled = False
mediamtx_process = None
audio_process = None

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

def stop_audio_stream():
    global audio_process
    if audio_process:
        audio_process.terminate()
        audio_process = None
    stop_loudness_worker()

@bp.route("/")
def index():
    global video_enabled, audio_enabled

    # Decide which stream to show
    if video_enabled and audio_enabled:
        stream_path = "cam_with_audio"
    elif video_enabled:
        stream_path = "cam"
        stop_audio_stream()  # stop audio if only video
    elif audio_enabled:
        stream_path = None
        stop_mediamtx()  # stop MediaMTX if only audio
    else:
        stream_path = None
        stop_mediamtx()
        stop_audio_stream()

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
    if video_enabled:
        start_mediamtx()
    else:
        stop_mediamtx
    return redirect(url_for("main.index"))

@bp.route("/toggle_audio")
def toggle_audio():
    global audio_enabled, audio_process
    audio_enabled = not audio_enabled
    if video_enabled and audio_enabled:
        start_mediamtx()
    elif audio_enabled and not video_enabled:
        stop_mediamtx()
        stop_audio_stream() # Kill old process if running
        audio_process = subprocess.Popen([
            'ffmpeg',
            '-f', 'alsa',
            '-ac', '1',
            '-ar', '44100',
            '-sample_fmt', 's16',
            '-i', 'plughw:0,0',
            '-c:a', 'libopus',
            '-b:a', '32000',
            '-content_type', 'audio/ogg',
            '-f', 'ogg',
            'icecast://source:hackme@localhost:8000/audio.ogg'
        ])
        start_loudness_worker(device='plughw:0,0', sample_interval=1.0, duration=0.5, samplerate=44100)
    else:
        stop_audio_stream()
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