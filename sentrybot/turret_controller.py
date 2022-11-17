"""Module for moving, and streaming video from, the physical turret."""
from time import sleep

import gpiozero


class RangeOfMovementError(Exception):
    """When an invalid horizontal or vertical angle is requested."""


class TurretController:
    """Controls for the physical turret."""

    def __init__(self) -> None:
        self._x_servo = gpiozero.Servo(
            13, pin_factory=gpiozero.pins.pigpio.PiGPIOFactory()
        )
        self._y_servo = gpiozero.Servo(
            12, pin_factory=gpiozero.pins.pigpio.PiGPIOFactory()
        )
        self._breach_servo = gpiozero.Servo(
            26, pin_factory=gpiozero.pins.pigpio.PiGPIOFactory()
        )

    def set_x(self, value: float) -> None:
        """Set the current objective x value."""

        # if not -1 <= value <= 1:
        if not -0.5 <= value <= 0.5:
            raise RangeOfMovementError
        self._x_servo.value = 1

    def set_y(self, value: float) -> None:
        """Set the current objective y value."""

        # if not -1 <= value <= 1:
        if not -0.5 <= value <= 0.5:
            raise RangeOfMovementError

    def launch(self) -> None:
        """Blocks until the turret has fired."""

        self._breach_servo.value = -0.5

        # ToDo Is this necessary?
        sleep(0.01)

        self._breach_servo.value = 0
