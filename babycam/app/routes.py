from flask import Blueprint, render_template, redirect, url_for
import subprocess
import os

bp = Blueprint("main", __name__)

# Global variable to track stream process
stream_process = None

@bp.route("/")
def index():
    # Get CPU temp
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_c = int(f.read()) / 1000
    except:
        temp_c = None
    streaming = stream_process is not None
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