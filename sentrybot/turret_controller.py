"""Module for moving, and streaming video from, the physical turret."""
from gpiozero import Servo


class RangeOfMovementError(Exception):
    """When an invalid horizontal or vertical angle is requested."""


class TurretController:
    """Controls for the physical turret."""

    def __init__(self) -> None:
        self._x_servo = Servo()
        self._y_servo = Servo()

    def set_x(self, value: float) -> None:
        """Set the current objective x value."""
        if not -1 <= value <= 1:
            raise RangeOfMovementError
        self._x_servo.value = 1

    def set_y(self, value: float) -> None:
        """Set the current objective y value."""
        if not 0 <= value <= 1:
            raise RangeOfMovementError
