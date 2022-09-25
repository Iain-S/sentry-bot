"""App factory module."""
from datetime import datetime
from pathlib import Path
from typing import List, Mapping, Optional

import toml
from flask import Flask, Response, abort, render_template, request, send_from_directory

from sentrybot.video import generate_face_detection_video, generate_video


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    """Create and configure the app."""
    # pylint: disable=inconsistent-return-statements
    mouse_position: List[int] = []

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        # Expect the config file to be in the current working directory
        app.config.from_file(
            str(Path(".").resolve() / "config.toml"),
            load=toml.load,  # silent=True
        )
    else:
        app.config.from_mapping(test_config)

    @app.route("/video")
    def video() -> str:
        return render_template("video.html")

    @app.route("/face-detection")
    def face_detection() -> str:
        return render_template("face_detection.html")

    @app.route("/face-detected-video-feed")
    def face_detected_video() -> Response:
        return Response(
            generate_face_detection_video(mouse_position),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    @app.route("/video-feed")
    def video_feed() -> Response:
        video_path = app.config["VIDEO_PATH"]
        return Response(
            generate_video(video_path),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.route("/send-receive")
    def send_receive() -> str:
        return render_template("send_receive.html")

    @app.route("/ajax-data", methods=["POST", "GET"])
    def ajax_data() -> dict:
        if request.method == "POST":
            if request.json and "xPos" in request.json and "yPos" in request.json:
                mouse_position[0:2] = [
                    int(round(request.json["xPos"], 0)),
                    int(round(request.json["yPos"], 0)),
                ]
                return {}

            abort(404, description="One or more of xPos and yPos are missing")
        else:
            # Return a dict, which will be jsonified automatically
            return {"theDate": datetime.now()}

    @app.route("/game")
    def game() -> str:
        return render_template("game.html")

    @app.route("/TemplateData/<path:path>")
    def send_template_data(path: str) -> Response:
        return send_from_directory("static/TemplateData", path)

    @app.route("/Build/<path:path>")
    def send_build(path: str) -> Response:
        return send_from_directory("static/Build", path)

    @app.route("/StreamingAssets/<path:path>")
    def send_streaming_assets(path: str) -> Response:
        return send_from_directory("static/StreamingAssets", path)

    return app
