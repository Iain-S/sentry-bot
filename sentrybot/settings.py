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
    control_turret: bool
    do_aiming: bool
    minimum_hue_target: int = 0
    maximum_hue_target: int = 60
    streaming_source: int = 2
    firing_threshold: int = 20
    frame_delay: float = 0.03
