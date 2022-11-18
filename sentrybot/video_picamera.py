"""Generators for video streams that use a Raspberry Pi camera."""
import os
from typing import Generator, List
import picamera
import io
from threading import Condition

RESOLUTION = os.environ.get('RESOLUTION', '640x480')
FRAMERATE = int(os.environ.get('FRAMERATE', 24))
ROTATION = int(os.environ.get('ROTATION', 0))

if ROTATION not in [0, 90, 180, 270]:
    ROTATION = 0

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

 
def generate_file_video(video_path: str) -> Generator[bytes, None, None]:
    """Generate a video stream from a file."""
    del video_path
    yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray() + b"\r\n"


def generate_camera_video(
    mouse_position: List[int],
) -> Generator[bytes, None, None]:
    """Generate a video stream from a Raspberry Pi camera."""
    with picamera.PiCamera(resolution='%s' % RESOLUTION,
                       framerate=FRAMERATE) as camera:
        camera.rotation = ROTATION
        camera.annotate_background = picamera.Color('black')
        #camera.annotate_text = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')

        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')

        while True:
            #self.server.camera.annotate_text = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
            with output.condition:
                output.condition.wait()
                frame = output.frame
            #self.wfile.write(b'--FRAME\r\n')
            #self.send_header('Content-Type', 'image/jpeg')
            #self.send_header('Content-Length', len(frame))
            #self.end_headers()
            #self.wfile.write(frame)
            #self.wfile.write(b'\r\n')
            yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray(frame) + b"\r\n"

    del mouse_position
