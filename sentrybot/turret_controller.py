"""Module for moving, and streaming video from, the physical turret."""
from time import sleep

from gpiozero import Servo  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore


class RangeOfMovementError(Exception):
    """When an invalid horizontal or vertical angle is requested."""


class TurretController:
    """Controls for the physical turret."""

    def __init__(self) -> None:
        self._x_servo = Servo(13, pin_factory=PiGPIOFactory())
        self._y_servo = Servo(12, pin_factory=PiGPIOFactory())
        self._breach_servo = Servo(26, pin_factory=PiGPIOFactory())

    def set_x(self, value: float) -> None:
        """Set the current objective x value."""

        # if not -1 <= value <= 1:
        if not -0.5 <= value <= 0.5:
            raise RangeOfMovementError
        self._x_servo.value = value

    def set_y(self, value: float) -> None:
        """Set the current objective y value."""

        # if not -1 <= value <= 1:
        if not -0.5 <= value <= 0.5:
            raise RangeOfMovementError

        self._y_servo.value = value

    def launch(self) -> None:
        """Blocks until the turret has fired."""

        self._breach_servo.value = -0.5

        # May, or may not, be necessary
        sleep(0.01)

        self._breach_servo.value = 0
