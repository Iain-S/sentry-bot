"""Recognise and aim with haar cascades."""
from typing import Optional

import numpy as np

from sentrybot.turret_controller import TurretController


def calc_distance() -> float:
    """Calculate distance to the ball in rect."""
    pass


def do_haar_aiming(
    frame: np.ndarray, turret: Optional[TurretController], state: dict
) -> np.ndarray:
    """Aim and fire at any balls in frame."""

    state["a"] = state.get("a", 0) + 1
    return frame
