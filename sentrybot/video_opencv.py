"""Generators for video streams that use OpenCV."""
import logging
from pathlib import Path
from time import sleep
from typing import Generator, List

import cv2


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


def generate_camera_video(
    mouse_position: List[int],
) -> Generator[bytes, None, None]:
    """Generate a video stream from a camera, with face detection rectangles."""
    # pylint: disable=no-member,invalid-name,too-many-locals

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

        frame = cv2.resize(frame, (640, 360), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

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

        # Draw a dot where the mouse is
        if mouse_position:
            mouse_x = mouse_position[0]
            mouse_y = mouse_position[1]
            logging.debug("x:%s  y:%s", mouse_x, mouse_y)
            cv2.rectangle(
                frame,
                (mouse_x, mouse_y),
                (mouse_x + 10, mouse_y + 10),
                (255, 0, 0),
                4,
            )

        # Encode the frame in JPEG format
        (flag, encoded_image) = cv2.imencode(".jpg", frame)

        # Ensure the frame was successfully encoded
        if flag:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encoded_image) + b"\r\n"
            )
