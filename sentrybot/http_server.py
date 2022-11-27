import io
import logging
import socketserver
from http import server
from threading import Condition

import picamera  # type: ignore # pylint: disable=import-error

from sentrybot.turret_controller import TurretController

turret_controller = TurretController()

PAGE = """\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<script>
    function handleMouseClick(event) {
        console.log("mouse click");
        const req = new XMLHttpRequest();
        req.addEventListener("load", (event) => {
            console.log("Mouse movements successfully sent");
        });
        req.open("GET", "/ajax-data");
        const params = JSON.stringify({
            "key": "value",
        });
        req.setRequestHeader("Content-type", "application/json; charset=utf-8");
        req.send(params);
    }
    window.onload = () => {
        const box = document.querySelector(".etch-a-sketch");
        box.onclick = (event) => {
            handleMouseClick(event);
        }
    }
</script>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
<div class="etch-a-sketch" style="background-color: #EBEBEB;" width="640" height="480">
ajax_data
<div>
</body>
</html>
"""


class StreamingOutput:
    def __init__(self) -> None:
        self.frame = bytes()
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf: bytes) -> int:
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
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
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
                raise
        elif self.path == "/ajax-data":
            logging.warning("received ajax data")
            turret_controller.launch()
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with picamera.PiCamera(resolution="640x480", framerate=24) as camera:

    output = StreamingOutput()
    camera.start_recording(output, format="mjpeg")
    try:
        address = ("", 8000)
        my_server = StreamingServer(address, StreamingHandler)
        logging.warning("serving")
        my_server.serve_forever()
    finally:
        camera.stop_recording()
