"""An autonomous sentry turret."""
import logging
import os
from pathlib import Path
from time import sleep
from typing import Final, Generator, Mapping, Optional

import cv2
import toml
from flask import Flask, Response, render_template

__version__: Final = "0.1.0"


def generate_video(video_path: str) -> Generator[bytes, None, None]:
    """Generate a video stream from a file."""
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


def generate_face_detection_video() -> Generator[bytes, None, None]:
    """Generate a video stream from a camera, with face detection rectangles."""
    # pylint: disable=no-member,invalid-name

    # cv2 comes with cascade files
    casc_path = Path(cv2.__path__[0]) / "data/haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(str(casc_path))

    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            logging.warning("Can't receive frame (stream end?).")
            sleep(0.03)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode the frame in JPEG format
        (flag, encoded_image) = cv2.imencode(".jpg", frame)

        # Ensure the frame was successfully encoded
        if flag:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encoded_image) + b"\r\n"
            )


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    """Create and configure the app."""
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
            generate_face_detection_video(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.route("/")
    def index() -> str:
        # return the rendered template
        return render_template("index.html")

    @app.route("/video-feed")
    def video_feed() -> Response:
        # return the response generated along with the specific media
        # type (mime type)
        video_path = app.config["VIDEO_PATH"]
        return Response(
            generate_video(video_path),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    return app
