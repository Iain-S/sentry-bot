"""Mypy type stubs for the gpiozero package."""
from typing import Optional
from pins.pi import PiFactory



class Servo:
    value: float
    def __init__(self, pin_factory: Optional[PiFactory]=None) -> None:
        ...
