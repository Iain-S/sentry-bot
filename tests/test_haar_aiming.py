"""Tests for the haar aiming module."""
from sentrybot.haar_aiming import estimate_distance


def test_estimate_distance() -> None:
    """Test the package version."""
    assert estimate_distance(80_000) == 10.0
    assert estimate_distance(20_000) == 20.0
    assert estimate_distance(800) == 100.0
