from flask import Blueprint, render_template, redirect, url_for
import subprocess
import os

bp = Blueprint("main", __name__)

# Global variable to track stream process
stream_process = None

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except:
        return None

@bp.route("/")
def index():
    streaming = stream_process is not None
    temp_c = get_cpu_temp()
    return render_template("index.html", streaming=streaming, temp_c=temp_c)

@bp.route("/toggle")
def toggle_stream():
    global stream_process
    if stream_process is None:
        # Start MediaMTX
        stream_process = subprocess.Popen(
            ["./mediamtx"]
        )
    else:
        # Stop MediaMTX
        stream_process.terminate()
        stream_process = None
    return redirect(url_for("main.index"))

@bp.route("/temperature")
def temperature():
    """Return current CPU temperature for AJAX refresh"""
    return str(get_cpu_temp())