"""Unit tests for the server module."""
from sentrybot import settings


def test_settings() -> None:
    """Test the server settings."""
    settings.Settings(
        camera_library=settings.CameraLibrary.OPENCV,
        control_turret=False,
        do_aiming=False,
        _env_file=None,
    )
