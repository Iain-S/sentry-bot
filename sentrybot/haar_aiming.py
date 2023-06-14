"""Recognise and aim with haar cascades."""
import math
from pathlib import Path
from typing import Optional, Tuple

import cv2  # type: ignore
import numpy as np

from sentrybot.turret_controller import TurretController

# pylint: disable=fixme,unused-argument


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
    casc_path = Path(cv2.__path__[0]) / "data/haarcascade_frontalface_default.xml"

    ball_cascade = cv2.CascadeClassifier(str(casc_path))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ToDo How tune these params.
    balls = ball_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(10, 10),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    # Draw a rectangle around the balls
    for x, y, w, h in balls:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # balls is an empty tuple if there are none
    if isinstance(balls, np.ndarray) and balls.any():
        x, y, w, h = balls[0]

        frame_centre = int(frame.shape[1] / 2), int(frame.shape[0] / 2)
        ball_centre = int(x + (w / 2)), int(y + (h / 2))
        cv2.line(frame, frame_centre, ball_centre, (255, 0, 0), 10)

        move_toward_target(frame, frame_centre, ball_centre, turret, state)

        if 240 < x + (w * 0.5) < 400 and 130 < y + (h * 0.5) < 230:
            # Target in middle of frame (assuming a 640x360 resolution)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return frame


def move_toward_target(
    frame: np.ndarray,
    frame_centre: Tuple,
    target_centre: Tuple,
    turret: Optional[TurretController],
    state: dict,
) -> None:
    """Move turret to point at target."""

    # -ve means target to left, +ve target to right
    x_distance = -1 * (target_centre[0] - frame_centre[0])

    # -ve means target below, +ve target above
    y_distance = -1 * (target_centre[1] - frame_centre[1])

    # ToDo Fine tune these
    x_nudge = x_distance / 1_000
    y_nudge = y_distance / 1_000
    # logging.warning("%s, %s", x_nudge, y_nudge)

    if turret:
        turret.nudge_x(x_nudge)
        turret.nudge_y(y_nudge)
