"""Generators for video streams that use OpenCV."""
import logging
from pathlib import Path
from threading import Event, Thread
from time import sleep
from typing import Generator, Optional

import cv2  # type: ignore
import numpy

from sentrybot.client_instruction import ClientInstruction
from sentrybot.http_server import StreamingOutput
from sentrybot.turret_controller import TurretController


def generate_file_video(video_path: str) -> Generator[bytes, None, None]:
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


def do_aiming(
    frame: numpy.ndarray, turret_controller: Optional[TurretController]
) -> None:
    """Find a target and aim the turret at it.

    Presume that we are called with each and every camera frame.
    """
    # pylint: disable=no-member,unused-argument

    # cv2 comes with cascade files
    casc_path = Path(cv2.__path__[0]) / "data/haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(str(casc_path))

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

    # faces is an empty tuple if there are none
    if isinstance(faces, numpy.ndarray) and faces.any():

        x, y, w, h = faces[0]

        if 240 < x + (w * 0.5) < 400 and 130 < y + (h * 0.5) < 230:
            # Target in middle of frame (assuming a 640x360 resolution)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)


def generate_camera_video(
    turret_instruction: Optional[ClientInstruction] = None,
    turret_controller: Optional[TurretController] = None,
) -> Generator[bytes, None, None]:
    """Generate a video stream from a camera, with face detection rectangles."""
    # pylint: disable=no-member,invalid-name

    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            logging.warning("Can't receive frame (stream end?).")
            sleep(0.03)

        frame = cv2.resize(frame, (640, 360), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

        do_aiming(frame, turret_controller)

        # Draw a dot where the mouse is
        if turret_instruction:
            mouse_x = turret_instruction.x_pos
            mouse_y = turret_instruction.y_pos
            logging.debug("x:%s  y:%s", mouse_x, mouse_y)
            # cv2.rectangle(
            #     frame,
            #     (mouse_x, mouse_y),
            #     (mouse_x + 10, mouse_y + 10),
            #     (255, 0, 0),
            #     4,
            # )

        # Encode the frame in JPEG format
        (flag, encoded_image) = cv2.imencode(".jpg", frame)

        # Ensure the frame was successfully encoded
        if flag:
            yield bytearray(encoded_image)


class OpenCVCamera:
    """A class to push camera frames in a background thread."""

    # pylint: disable=redefined-builtin

    def __init__(self, turret_controller: Optional[TurretController]) -> None:
        self.should_exit = Event()
        self.thread: Optional[Thread] = None
        self.turret_controller = turret_controller

    def record_to(self, output: StreamingOutput, should_exit: Event) -> None:
        """Send OpenCV video to output."""

        # ToDo Restore client instruction?
        stream = generate_camera_video(None, self.turret_controller)
        while not should_exit.is_set():
            try:
                frame = next(stream)
                output.write(frame)
            except StopIteration:
                print("Stopping...")
                break

    def start_recording(self, output: StreamingOutput, format: str = "") -> None:
        """Match PiCamera's method signature."""
        del format

        # Start recording in the background
        self.should_exit = Event()
        self.thread = Thread(target=self.record_to, args=(output, self.should_exit))
        self.thread.start()

    def stop_recording(self) -> None:
        """Stop writing frames and exit the background thread."""
        self.should_exit.set()
        if not self.thread:
            raise RuntimeError("stop_recording() called before start_recording()")
        self.thread.join(1.0)
