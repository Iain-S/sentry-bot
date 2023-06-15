"""Configuration via environment variables."""
from enum import Enum

from pydantic import BaseSettings


class CameraLibrary(str, Enum):
    """Supported camera libraries."""

    PICAMERA = "picamera"
    OPENCV = "opencv"


class Settings(BaseSettings):
    """Environment variable settings."""

    camera_library: CameraLibrary
    control_turret: bool  # Try to move the turret
    minimum_hue_target: int = 0  # For the tennis ball, keep hue between 0 and 60.
    maximum_hue_target: int = 60
    minimum_value_target: int = 0  # For the cat, values should be between 0 and 30
    maximum_value_target: int = 255
    streaming_source: int = 2  # 0 for raw camera output
    do_haar_aiming: bool = False
    firing_threshold: int = 20  # 10+ for half-distance targets
    frame_delay: float = 0.03
    default_nudge: float = 0.1  # 0.04 for fine-tuning aiming.
    rotate_feed: bool = True  # Rotate the camera feed
    camera_offset: int = 100  # 175 for mid distance balls
