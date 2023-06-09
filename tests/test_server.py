"""Unit tests for the server module."""
import sentrybot.http_server as server


def test_settings() -> None:
    """Test the server settings."""
    server.Settings(
        camera_library=server.CameraLibrary.OPENCV,
        control_turret=False,
        _env_file=None,
    )
