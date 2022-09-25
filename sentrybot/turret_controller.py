"""Module for moving, and streaming video from, the physical turret."""
from gpiozero import Servo


class RangeOfMovementError(Exception):
    """When an invalid horizontal or vertical angle is requested."""


class TurretController:
    """Controls for the physical turret."""

    def __init__(self) -> None:
        self._x: float = 0
        self._y: float = 0

    @property
    def x(self) -> float:
        """Get the current objective x value."""
        return self._x

    @x.setter
    def x(self, degrees: float) -> None:
        """Set the current objective x value."""
        if not -90 <= degrees <= 90:
            raise RangeOfMovementError

        pwm = Servo()
        pwm.value = 90
        self._x = degrees

    @property
    def y(self) -> float:
        """Get the current objective y value."""
        return self._y

    @y.setter
    def y(self, degrees: float) -> None:
        """Set the current objective y value."""
        if not -10 <= degrees <= 90:
            raise RangeOfMovementError
        self._y = degrees
