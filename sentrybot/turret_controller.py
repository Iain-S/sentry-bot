"""Module for moving, and streaming video from, the physical turret."""
from time import sleep

from gpiozero import OutputDevice, Servo  # type: ignore
from gpiozero.pins.pigpio import PiGPIOFactory  # type: ignore


class RangeOfMovementError(Exception):
    """When an invalid horizontal or vertical angle is requested."""


class TurretController:
    """Controls for the physical turret."""

    def __init__(self) -> None:
        self._x_servo = Servo(12, pin_factory=PiGPIOFactory())
        self._y_servo = Servo(13, pin_factory=PiGPIOFactory())

        self._right_dc_motor = OutputDevice(26, pin_factory=PiGPIOFactory())
        self._left_dc_motor = OutputDevice(5, pin_factory=PiGPIOFactory())

        self._breach_servo = Servo(17, pin_factory=PiGPIOFactory())

    def set_x(self, value: float) -> None:
        """Set the horizontal rotation.

        Args:
            value: -1 for down, +1 for up and all the values in-between.
        """

        # Just while we're testing
        value = max(min(0.9, value), -0.9)
        # While we're testing

        # Try to be more efficient by only setting when we need to
        if self._x_servo.value != round(value, 14):
            self._x_servo.value = value

    def set_y(self, value: float) -> None:
        """Set the vertical rotation.

        Args:
            value: -1 for left, +1 for right and all the values in-between.
        """
        if not -1 <= value <= 1:
            # raise RangeOfMovementError
            print("yerror: ", value)

        # Just while we're testing
        value = max(min(0.9, value), -0.9)
        # While we're testing

        # Try to be more efficient by only setting when we need to
        if self._y_servo.value != round(value, 14):
            self._y_servo.value = value

    def launch(self) -> None:
        """Blocks until the turret has fired."""

        self._right_dc_motor.on()
        # May, or may not, be the right length of time
        sleep(1.0)
        # By activating the motors in turn, we hope to minimise voltage sag
        self._left_dc_motor.on()
        sleep(1.0)

        self._breach_servo.value = -0.8

        # May, or may not, be the right length of time
        sleep(0.5)

        self._breach_servo.value = 0
        sleep(0.5)
        # This software-PCM-controlled servo is best detached when not in use
        # to reduce mechanical noise and, hopefully, save CPU cycles
        self._breach_servo.detach()

        self._right_dc_motor.off()
        self._left_dc_motor.off()

    def reset(self) -> None:
        """Blocks until servos have been reset to their starting positions."""
        self.set_x(0)
        self.set_y(0)
        self._breach_servo.value = 0
        sleep(0.5)
        self._breach_servo.detach()
