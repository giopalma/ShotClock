from flask import Flask, Response
from device.api.video import frame_stream

app = Flask(__name__)


@app.route("/video")
def video_feed():
    return Response(
        frame_stream(), content_type="multipart/x-mixed-replace; boundary=frame"
    )


def run(debug: bool):
    app.run(debug=debug)
