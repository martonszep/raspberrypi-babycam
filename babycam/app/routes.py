from flask import Blueprint, render_template, Response
from .stream import mjpeg_generator

bp = Blueprint("main", __name__)

streaming_enabled = False

@bp.route("/")
def index():
    return render_template("index.html", streaming=streaming_enabled)

@bp.route("/video_feed")
def video_feed():
    if streaming_enabled:
        return Response(mjpeg_generator(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")
    return "Streaming is off"

@bp.route("/toggle")
def toggle_stream():
    global streaming_enabled
    streaming_enabled = not streaming_enabled
    return f"Streaming {'enabled' if streaming_enabled else 'disabled'}"