"""Tests for the turret_controller module.

Remember to patch gpiozero imports on every test function.
Otherwise, it will complain that it cannot find the Raspberry Pi hardware."""
from unittest.mock import MagicMock, call, patch

import pytest

from sentrybot.turret_controller import RangeOfMovementError, TurretController


@patch("sentrybot.turret_controller.PiGPIOFactory")
@patch("sentrybot.turret_controller.Servo")
def test_turret_controller_properties(_: MagicMock, __: MagicMock) -> None:
    """Test that we can call the getters and setters."""
    turret_controller = TurretController()

    turret_controller.set_x(1)
    turret_controller.set_x(-1)

    turret_controller.set_y(1)
    turret_controller.set_y(0)


@pytest.mark.xfail
@patch("sentrybot.turret_controller.PiGPIOFactory")
@patch("sentrybot.turret_controller.Servo")
def test_turret_controller_raises(_: MagicMock, __: MagicMock) -> None:
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


@patch("sentrybot.turret_controller.PiGPIOFactory")
@patch("sentrybot.turret_controller.OutputDevice")
@patch("sentrybot.turret_controller.Servo")
def test_turret_controller_output_devices(
    servo: MagicMock, output_device: MagicMock, pigpio_factory: MagicMock
) -> None:
    """Test that servos are activated as they should be."""
    mock_x, mock_y, mock_breach = MagicMock(), MagicMock(), MagicMock()
    servo.side_effect = [mock_x, mock_y, mock_breach]
    turret_controller = TurretController()

    # More to do here, see
    # https://gpiozero.readthedocs.io/en/stable/api_output.html?highlight=servo#gpiozero.Servo
    servo.assert_has_calls(
        [
            call(12, pin_factory=pigpio_factory()),
            call(13, pin_factory=pigpio_factory()),
            call(17, pin_factory=pigpio_factory()),
        ]
    )

    output_device.assert_has_calls(
        [
            call(26, pin_factory=pigpio_factory()),
            call(5, pin_factory=pigpio_factory()),
        ]
    )

    turret_controller.set_x(0.1)
    assert mock_x.value == 0.1

    turret_controller.set_y(0.1)
    assert mock_y.value == 0.1

    turret_controller.launch()
    mock_breach.assert_has_calls(
        [
            call.detach(),
        ]
    )
