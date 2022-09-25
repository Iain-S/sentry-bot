"""Tests for the turret_controller module."""
from unittest.mock import MagicMock, call, patch

import pytest

from sentrybot.turret_controller import RangeOfMovementError, TurretController


def test_turret_controller_properties() -> None:
    """Test that we can call the getters and setters."""
    turret_controller = TurretController()

    turret_controller.set_x(1)
    turret_controller.set_x(-1)

    turret_controller.set_y(1)
    turret_controller.set_y(0)


def test_turret_controller_raises() -> None:
    """Test that errors are raised for invalid angles."""
    turret_controller = TurretController()

    with pytest.raises(RangeOfMovementError):
        turret_controller.set_x(1.1)
    with pytest.raises(RangeOfMovementError):
        turret_controller.set_x(-1.1)

    with pytest.raises(RangeOfMovementError):
        turret_controller.set_y(1.1)
    with pytest.raises(RangeOfMovementError):
        turret_controller.set_y(-0.1)


@patch("sentrybot.turret_controller.Servo")
def test_turret_controller_output_devices(servo: MagicMock) -> None:
    """Test that servos are activated as they should be."""
    TurretController()

    # More to do here, see
    # https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=servo#gpiozero.Servo
    servo.assert_has_calls(
        [
            call(),
            call(),
        ]
    )
