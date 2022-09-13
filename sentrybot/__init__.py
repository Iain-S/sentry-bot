"""An autonomous sentry turret."""
import logging
from pathlib import Path
from typing import Final, Generator, Mapping, Optional

import cv2
import toml
from flask import Flask, Response, render_template

__version__: Final = "0.1.0"


def generate_video(video_path: str) -> Generator[bytes, None, None]:
    """Generate a video stream."""
    # pylint: disable=no-member
    while True:
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.warning("Can't receive frame (stream end?).")
                break

            # Adjust for best performance
            frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)

            # Encode the frame in JPEG format
            (flag, encoded_image) = cv2.imencode(".jpg", frame)
            # Ensure the frame was successfully encoded
            if flag:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + bytearray(encoded_image)
                    + b"\r\n"
                )


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=Path(app.instance_path) / "flaskr.sqlite",
    )

    # ensure the instance folder exists
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file(
            str(Path(app.instance_path) / "config.toml"),
            load=toml.load,
            # silent=True
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.route("/hello")
    def hello() -> str:
        # a simple page that says hello
        return "Hello, World!"

    @app.route("/")
    def index() -> str:
        # return the rendered template
        return render_template("index.html")

    @app.route("/video_feed")
    def video_feed() -> Response:
        # return the response generated along with the specific media
        # type (mime type)
        video_path = app.config["VIDEO_PATH"]
        return Response(
            generate_video(video_path),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    return app
