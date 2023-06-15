# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=no-member

"""Generators for video streams that use OpenCV."""
import logging
import time

# import time
from threading import Event, Thread
from time import sleep
from typing import Generator, Optional

import cv2  # type: ignore
import numpy

from sentrybot.client_instruction import ClientInstruction
from sentrybot.haar_aiming import do_haar_aiming
from sentrybot.hsv_aiming import do_mask_based_aiming
from sentrybot.http_server import StreamingOutput
from sentrybot.settings import Settings
from sentrybot.turret_controller import TurretController

# pylint: disable=fixme,unused-argument


def _draw_vertical_line(
    streaming_frame: numpy.ndarray, x_position: float, height: float
) -> None:
    # print(f"{x_position=}")
    cv2.line(
        streaming_frame,
        (int(x_position), 0),
        (int(x_position), height),
        (255, 0, 0),
        thickness=2,
    )


def generate_camera_video(
    turret_instruction: Optional[ClientInstruction] = None,
    turret_controller: Optional[TurretController] = None,
) -> Generator[bytes, None, None]:
    """Generate a video stream from a camera, with face detection rectangles."""
    # pylint: disable=no-member,invalid-name

    settings = Settings()

    video_capture = cv2.VideoCapture(0)

    # For aiming state between frames
    state: dict = {}

    projectile_launched: bool = False
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            logging.warning("Can't receive frame (stream end?).")
            sleep(Settings().frame_delay)

        frame = cv2.resize(
            frame, (0, 0), fx=0.3, fy=0.3, interpolation=cv2.INTER_LINEAR
        )

        # The robot's camera is mounted sideways
        if settings.rotate_feed:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # do_aiming(frame, turret_controller)
        if settings.do_aiming and not projectile_launched:
            if settings.do_haar_aiming:
                do_haar_aiming(frame, turret_controller, state)
            else:
                minimum_hue: int = settings.minimum_hue_target
                maximum_hue: int = settings.maximum_hue_target
                minimum_value: int = settings.minimum_value_target
                maximum_value: int = settings.maximum_value_target

                frame, projectile_launched = do_mask_based_aiming(
                    frame,
                    turret_controller,
                    minimum_hue=minimum_hue,
                    maximum_hue=maximum_hue,
                    minimum_value=minimum_value,
                    maximum_value=maximum_value,
                )

        # Draw a dot where the mouse is
        if turret_instruction:
            mouse_x = turret_instruction.x_pos
            mouse_y = turret_instruction.y_pos
            logging.debug("x:%s  y:%s", mouse_x, mouse_y)

        # Encode the frame in JPEG format
        (flag, encoded_image) = cv2.imencode(
            ".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, 100)
        )

        # Ensure the frame was successfully encoded
        if flag:
            yield bytearray(encoded_image)
            time.sleep(settings.frame_delay)


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
