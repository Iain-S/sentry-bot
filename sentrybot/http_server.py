"""A webserver to control the robot."""
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# pylint: disable=import-error
# pylint: disable=fixme
import io
import logging
import socketserver
from http import server
from pathlib import Path
from threading import Condition
from typing import Any, Final, Optional, Union
from urllib.parse import parse_qs

from sentrybot.settings import CameraLibrary, Settings
from sentrybot.turret_controller import TurretController

with (Path(__file__).parent.resolve() / "templates/simpleserver.html").open(
    "r", encoding="utf-8"
) as the_file:
    PI_RECOGNITION_PAGE: Final[str] = the_file.read()

with (Path(__file__).parent.resolve() / "templates/offload.html").open(
    "r", encoding="utf-8"
) as the_file:
    LAPTOP_RECOGNITION_PAGE: Final[str] = the_file.read()

with (Path(__file__).parent.resolve() / "templates/index.html").open(
    "r", encoding="utf-8"
) as the_file:
    LANDING_PAGE: Final[str] = the_file.read()

with (Path(__file__).parent.resolve() / "templates/mask.html").open(
    "r", encoding="utf-8"
) as the_file:
    MASK_RECOGNITION_PAGE: Final[str] = the_file.read()


class StreamingOutput:
    """Implements a write() method for PiCamera to send video to."""

    def __init__(self) -> None:
        self.frame = bytes()
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf: bytes) -> int:
        """Write the bytes to a buffer and notify clients."""
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


OUTPUT: Final[StreamingOutput] = StreamingOutput()


class StreamingHandler(server.SimpleHTTPRequestHandler):
    """Handle HTTP requests."""

    # pylint: disable=too-many-branches,too-many-statements

    turret: Optional[TurretController] = None
    camera: Optional[Any] = None

    @classmethod
    def set_turret(cls, turret: TurretController) -> None:
        """Set a turret controller."""
        cls.turret = turret

    @classmethod
    def set_camera(
        cls,
        camera: Any,
    ) -> None:
        """Set a turret controller."""
        cls.camera = camera

    def do_GET(self) -> None:
        assert self.camera, "self.camera should not be None"

        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()

        elif self.path == "/index.html":
            content = LANDING_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/pi_processing.html":
            content = PI_RECOGNITION_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/laptop_processing.html":
            content = LAPTOP_RECOGNITION_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/mask_processing.html":
            content = MASK_RECOGNITION_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.camera.start_recording(OUTPUT, format="mjpeg")
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
            self.end_headers()
            try:
                while True:
                    with OUTPUT.condition:
                        OUTPUT.condition.wait()
                        frame = OUTPUT.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except BrokenPipeError:
                # Presume the browser page was closed
                logging.warning("Connection lost.")
                self.camera.stop_recording()
                return
            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
                raise
        elif self.path.startswith("/ajax-data"):
            parsed = parse_qs(self.path[len("/ajax-data?") :])
            logging.warning("received ajax data: %s", parsed)

            if self.turret:
                if "shouldFire" in parsed and parsed["shouldFire"][0]:
                    self.turret.launch()

                elif "xPos" in parsed and "yPos" in parsed:
                    self.turret.set_x(float(parsed["xPos"][0]))
                    self.turret.set_y(float(parsed["yPos"][0]))

                elif "xNudge" in parsed and "yNudge" in parsed:
                    self.turret.nudge_x(-1 * float(parsed["xNudge"][0]))
                    self.turret.nudge_y(float(parsed["yNudge"][0]))

            # Still getting ERR_EMPTY_RESPONSE
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            self.wfile.write(b"")

        elif self.path.startswith("/set_desired_coords"):
            parsed = parse_qs(self.path[len("/set_desired_coords?") :])
            logging.warning("received ajax data: %s", parsed)
            if self.turret:
                if "shouldFire" in parsed and parsed["shouldFire"][0] == "true":
                    self.turret.launch()
                    logging.warning("FIRED")

                elif "xPos" in parsed and "yPos" in parsed:
                    self.turret.set_x(float(parsed["xPos"][0]))
                    self.turret.set_y(float(parsed["yPos"][0]))

            # Still getting ERR_EMPTY_RESPONSE
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            self.wfile.write(b"")

        elif self.path == "/latest-image.jpg":
            self.camera.start_recording(OUTPUT, format="mjpeg")
            with OUTPUT.condition:
                for _ in range(2):
                    OUTPUT.condition.wait()
                    frame = OUTPUT.frame
            # ToDo Remove one of these two send_response()s
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(frame)))
            self.end_headers()
            self.wfile.write(frame)
            self.send_response(200)
        else:
            # self.send_error(404)
            # self.end_headers()
            super().do_GET()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    """An HTTP server."""

    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    """Start a webserver to stream PiCamera video."""
    settings = Settings()
    turret = TurretController() if settings.control_turret else None

    if turret:
        StreamingHandler.set_turret(turret)

    if settings.camera_library is CameraLibrary.PICAMERA:
        import picamera  # type: ignore

        camera = picamera.PiCamera(resolution="640x480", framerate=24)
        camera.rotation = 270
    else:
        from sentrybot.video_opencv import OpenCVCamera

        camera = OpenCVCamera(turret)

    StreamingHandler.set_camera(camera)

    try:
        address = ("", 8000)
        my_server = StreamingServer(address, StreamingHandler)
        logging.warning("serving")
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.warning("exiting")
        camera.stop_recording()
        if turret:
            turret.reset()


if __name__ == "__main__":
    main()
