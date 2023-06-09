"""A webserver to control the robot."""
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-import
# pylint: disable=import-error
import io
import logging
import socketserver
from enum import Enum
from http import server
from pathlib import Path
from threading import Condition, Event, Thread
from typing import Final, Optional
from urllib.parse import parse_qs

from pydantic import BaseSettings

from sentrybot.turret_controller import TurretController


class CameraLibrary(str, Enum):
    """Supported camera libraries."""

    PICAMERA = "picamera"
    OPENCV = "opencv"


class Settings(BaseSettings):
    """Environment variable settings."""

    camera_library: CameraLibrary
    control_turret: bool


with (Path(__file__).parent.resolve() / "templates/simpleserver.html").open(
    "r", encoding="utf-8"
) as the_file:
    PAGE: Final[str] = the_file.read()


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

    turret: Optional[TurretController] = None

    @classmethod
    def set_turret(cls, turret: TurretController) -> None:
        """Set a turret controller."""
        cls.turret = turret

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
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

            # Still getting ERR_EMPTY_RESPONSE
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
    """Fire up a web server."""
    settings = Settings()

    turret = TurretController() if settings.control_turret else None

    if settings.camera_library is CameraLibrary.OPENCV:
        run_opencv(turret)

    else:
        run_picamera(turret)


def run_picamera(turret: Optional[TurretController]) -> None:
    """Start a webserver to stream PiCamera video."""
    import picamera  # type: ignore

    with picamera.PiCamera(resolution="640x480", framerate=24) as camera:

        camera.rotation = 270
        camera.start_recording(OUTPUT, format="mjpeg")
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


def record_to(output: StreamingOutput, should_exit: Event) -> None:
    """Send OpenCV video to output."""
    import sentrybot.video_opencv

    stream = sentrybot.video_opencv.generate_camera_video()
    while not should_exit.is_set():
        try:
            frame = next(stream)
            output.write(frame)
        except StopIteration:
            print("Stopping...")
            break


def run_opencv(turret: Optional[TurretController]) -> None:
    """Start a webserver to stream OpenCV video."""
    # Start recording in the background

    should_exit = Event()

    thread = Thread(target=record_to, args=(OUTPUT, should_exit))
    thread.start()

    try:
        port = 8000
        address = ("", 8000)
        my_server = StreamingServer(address, StreamingHandler)
        logging.warning("serving on %s", port)
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.warning("exiting")
        should_exit.set()
        if turret:
            turret.reset()
        thread.join(1.0)


if __name__ == "__main__":
    main()
