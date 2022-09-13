"""Unit tests for the sentrybot package."""
from sentrybot import __version__


def test_version():
    """Test the package version."""
    assert __version__ == "0.1.0"
