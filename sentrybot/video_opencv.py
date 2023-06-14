# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=no-member

"""Generators for video streams that use OpenCV."""
import logging
import time

# import time
from pathlib import Path
from threading import Event, Thread
from time import sleep
from typing import Any, Generator, List, Optional, Tuple

import cv2  # type: ignore
import numpy

from sentrybot.client_instruction import ClientInstruction
from sentrybot.haar_aiming import do_haar_aiming
from sentrybot.http_server import StreamingOutput
from sentrybot.settings import Settings
from sentrybot.turret_controller import TurretController

# pylint: disable=fixme,unused-argument


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


def _contour_to_rectangle(contour: Any) -> Tuple[int, int, int, int]:
    polygonal_curve = cv2.approxPolyDP(contour, 3, True)
    bounding_rectangle = cv2.boundingRect(polygonal_curve)

    return (
        bounding_rectangle[0],
        bounding_rectangle[1],
        bounding_rectangle[2],
        bounding_rectangle[3],
    )


def _detect_target(
    contours: List, minimum_target_area: float, maximum_target_area: float
) -> Optional[Any]:
    current_max_area: float = 0
    current_contour = None

    for contour in contours:
        # _, _, width, height = _contour_to_rectangle(contour)
        # area = width * height

        area = cv2.contourArea(contour)

        if area > current_max_area:
            current_max_area = area
            current_contour = contour
    if minimum_target_area < current_max_area < maximum_target_area:
        return current_contour

    return None


def _draw_contour(frame: numpy.ndarray, contour: Any) -> None:
    (
        contour_x,
        contour_y,
        contour_width,
        contour_height,
    ) = _contour_to_rectangle(contour)

    cv2.rectangle(
        frame,
        pt1=(contour_x, contour_y),
        pt2=(contour_x + contour_width, contour_y + contour_height),
        color=(255, 0, 0),
        thickness=3,
    )
    cv2.drawContours(frame, [contour], 0, (0, 255, 0), 3)


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


def _aim(
    current_center_x: float,
    image_center_x: float,
    image_width: float,
    image_height: float,
    threshold: int,
    streaming_frame: numpy.ndarray,
    turret_controller: Optional[TurretController],
) -> None:
    # print(f"{image_width=}")

    right_threshold: float = image_center_x + image_width / threshold
    left_threshold: float = image_center_x - image_width / threshold

    _draw_vertical_line(streaming_frame, right_threshold, image_height)
    _draw_vertical_line(streaming_frame, left_threshold, image_height)

    default_left_nudge: float = 0.1

    if current_center_x > right_threshold and turret_controller:
        logging.warning("Object right")
        turret_controller.nudge_x(-default_left_nudge)

    elif current_center_x < left_threshold and turret_controller:
        logging.warning("Object left")
        turret_controller.nudge_x(default_left_nudge)

    else:
        logging.warning("Object at the center")


def do_mask_based_aiming(
    frame: numpy.ndarray,
    turret_controller: Optional[TurretController],
    minimum_hue: int = 30,
    maximum_hue: int = 50,
    minimum_parameter_value: int = 100,
    maximum_parameter_value: int = 255,
    minimum_target_area: int = 0,
    maximum_target_area: int = 100000,
    aim_threshold: int = 3,
) -> numpy.ndarray:
    """Aim with a HSV mask."""
    image_height, image_width, _ = frame.shape
    image_center_x: float = image_width / 2
    # image_center_y: float = image_height / 2

    hsv_frame: numpy.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bound: numpy.ndarray = numpy.array(
        [minimum_hue, minimum_parameter_value, minimum_parameter_value]
    )
    upper_bound: numpy.ndarray = numpy.array(
        [
            maximum_hue,
            maximum_parameter_value,
            maximum_parameter_value,
        ]  # Take a look at this. The original code had a bug here.
    )

    colour_mask: numpy.ndarray = cv2.inRange(hsv_frame, lower_bound, upper_bound)

    streaming_frame = frame
    if Settings().streaming_source == 1:
        streaming_frame = hsv_frame
    elif Settings().streaming_source == 2:
        streaming_frame = colour_mask

    contours, _ = cv2.findContours(colour_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    logging.warning("Detected contours: %s", str(len(contours)))

    contour_target = _detect_target(contours, minimum_target_area, maximum_target_area)

    if contour_target is None:
        logging.warning("No target detected")
    else:
        _draw_contour(streaming_frame, contour_target)

        position_x, _, width, _ = _contour_to_rectangle(contour_target)
        # current_max_area: float = width * height
        current_center_x: float = position_x + width / 2
        # current_center_y: float = position_y + height / 2

        _aim(
            current_center_x,
            image_center_x,
            image_width,
            image_height,
            aim_threshold,
            streaming_frame,
            turret_controller,
        )

    # e.g. turret_controller.nudge_x()

    return streaming_frame


def do_aiming(
    frame: numpy.ndarray, turret_controller: Optional[TurretController]
) -> None:
    """Find a target and aim the turret at it.

    Presume that we are called with each and every camera frame.
    """
    # pylint: disable=no-member,unused-argument

    # cv2 comes with cascade files
    # casc_path = Path(cv2.__path__[0]) / "data/haarcascade_frontalface_default.xml"
    casc_path = (
        Path(__file__).parent.resolve() / "cascades/cascade_12stages_24dim_0_25far.xml"
    )
    casc_path.exists()
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
    for x, y, w, h in faces:
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

    # For aiming state between frames
    state: dict = {}

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            logging.warning("Can't receive frame (stream end?).")
            sleep(0.03)

        frame = cv2.resize(frame, (640, 360), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

        # The robot's camera is mounted sideways
        # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if Settings().do_aiming:

            do_haar_aiming(frame, turret_controller, state)
        #     minimum_hue: int = Settings().minimum_hue_target
        #     maximum_hue: int = Settings().maximum_hue_target

        # Last working values: 0/60

        # minimum_hue: int = 0
        # maximum_hue: int = 60

        # frame = do_mask_based_aiming(
        #     frame,
        #     turret_controller,
        #     minimum_hue=minimum_hue,
        #     maximum_hue=maximum_hue,
        # )

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
        # start = time.perf_counter()
        (flag, encoded_image) = cv2.imencode(
            ".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, 100)
        )
        # logging.warning(time.perf_counter()-start)

        # Ensure the frame was successfully encoded
        if flag:
            yield bytearray(encoded_image)
            time.sleep(0.03)


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
