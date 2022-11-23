"""Utilities for sending instructions to the web server from a client."""
from dataclasses import dataclass


@dataclass
class ClientInstruction:
    """A container for instructions from client to server."""

    x_pos: int
    y_pos: int
    should_fire: bool
