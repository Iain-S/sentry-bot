"""Generators for video streams that use a Raspberry Pi camera."""
from typing import Generator, List


def generate_file_video(video_path: str) -> Generator[bytes, None, None]:
    """Generate a video stream from a file."""
    del video_path
    yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray() + b"\r\n"


def generate_camera_video(
    mouse_position: List[int],
) -> Generator[bytes, None, None]:
    """Generate a video stream from a Raspberry Pi camera."""
    del mouse_position
    yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray() + b"\r\n"
