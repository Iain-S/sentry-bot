"""Tests for the turret_controller module."""
from unittest.mock import patch

import pytest

from sentrybot.turret_controller import RangeOfMovementError, TurretController


def test_turret_controller_properties() -> None:
    """Test that we can call the getters and setters."""
    turret_controller = TurretController()

    assert turret_controller.x == 0
    turret_controller.x = 90
    assert turret_controller.x == 90
    turret_controller.x = -90
    assert turret_controller.x == -90

    assert turret_controller.y == 0
    turret_controller.y = 90
    assert turret_controller.y == 90
    turret_controller.y = -10
    assert turret_controller.y == -10


def test_turret_controller_raises() -> None:
    """Test that errors are raised for invalid angles."""
    turret_controller = TurretController()

    with pytest.raises(RangeOfMovementError):
        turret_controller.x = 91
    with pytest.raises(RangeOfMovementError):
        turret_controller.x = -91

    with pytest.raises(RangeOfMovementError):
        turret_controller.y = 91
    with pytest.raises(RangeOfMovementError):
        turret_controller.y = -11


@patch("sentrybot.turret_controller.Servo")
def test_turret_controller_output_devices(pwm_device) -> None:
    """Test that servos are activated as they should be."""
    turret_controller = TurretController()
    turret_controller.x = 90
    assert pwm_device.return_value.value == 90
