"""Recognise and aim with haar cascades."""
import logging
import math
from pathlib import Path
from typing import Optional

import cv2  # type: ignore
import numpy as np

from sentrybot.turret_controller import TurretController


def estimate_distance(area: int) -> float:
    """Calculate distance to the ball in rect.

    Uses heuristics and measurements."""
    x = area / 8000000.0
    y = 1 / x
    z = math.sqrt(y)
    return z


def do_haar_aiming(
    frame: np.ndarray, turret: Optional[TurretController], state: dict
) -> np.ndarray:
    """Find a target and aim the turret at it.

    Presume that we are called with each and every camera frame.
    """
    # pylint: disable=no-member,unused-argument

    casc_path = (
        Path(__file__).parent.resolve() / "cascades/cascade_12stages_24dim_0_25far.xml"
    )

    ball_cascade = cv2.CascadeClassifier(str(casc_path))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    balls = ball_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    # Draw a rectangle around the balls
    for x, y, w, h in balls:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # balls is an empty tuple if there are none
    if isinstance(balls, np.ndarray) and balls.any():
        x, y, w, h = balls[0]

        # logging.warning("h: %s, w: %s", h, w)
        logging.warning("area: %s", h * w)

        if 240 < x + (w * 0.5) < 400 and 130 < y + (h * 0.5) < 230:
            # Target in middle of frame (assuming a 640x360 resolution)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return frame
