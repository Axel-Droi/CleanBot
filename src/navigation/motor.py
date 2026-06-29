from __future__ import annotations

import time
from abc import ABC, abstractmethod


class MotorController(ABC):
    """Abstract interface for CleanBot drive motors + collection arm."""

    @abstractmethod
    def forward(self, speed: float = 1.0, duration: float = 0.5) -> None: ...

    @abstractmethod
    def turn_left(self, degrees: float = 90) -> None: ...

    @abstractmethod
    def turn_right(self, degrees: float = 90) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def collect(self) -> None: ...


class SimulatedMotorController(MotorController):
    """Drop-in replacement for hardware-free testing."""

    def forward(self, speed: float = 1.0, duration: float = 0.5) -> None:
        print(f"[SIM] FORWARD  speed={speed:.1f}  duration={duration}s")

    def turn_left(self, degrees: float = 90) -> None:
        print(f"[SIM] TURN_LEFT  {degrees}°")

    def turn_right(self, degrees: float = 90) -> None:
        print(f"[SIM] TURN_RIGHT  {degrees}°")

    def stop(self) -> None:
        print("[SIM] STOP")

    def collect(self) -> None:
        print("[SIM] COLLECT — actuating arm")


# ---------------------------------------------------------------------------
# Real hardware — Jetson Nano + L298N dual H-bridge motor driver
# Uncomment on target hardware and verify pin assignments against your wiring.
# ---------------------------------------------------------------------------
try:
    import Jetson.GPIO as GPIO  # type: ignore

    _BOARD_PINS = {
        "left_fwd":  11,
        "left_bwd":  12,
        "right_fwd": 13,
        "right_bwd": 15,
        "collect":   16,
    }
    _TURN_90_SECS = 0.6   # calibrate for your chassis
    _FWD_CELL_SECS = 0.4  # calibrate for your cell width

    class JetsonMotorController(MotorController):
        """L298N-based real motor controller for Jetson Nano (BOARD pin numbering)."""

        def __init__(self) -> None:
            GPIO.setmode(GPIO.BOARD)
            for pin in _BOARD_PINS.values():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        def forward(self, speed: float = 1.0, duration: float = _FWD_CELL_SECS) -> None:
            GPIO.output(_BOARD_PINS["left_fwd"],  GPIO.HIGH)
            GPIO.output(_BOARD_PINS["right_fwd"], GPIO.HIGH)
            time.sleep(duration / max(speed, 0.01))
            self.stop()

        def turn_left(self, degrees: float = 90) -> None:
            GPIO.output(_BOARD_PINS["right_fwd"], GPIO.HIGH)
            GPIO.output(_BOARD_PINS["left_bwd"],  GPIO.HIGH)
            time.sleep(_TURN_90_SECS * degrees / 90)
            self.stop()

        def turn_right(self, degrees: float = 90) -> None:
            GPIO.output(_BOARD_PINS["left_fwd"],  GPIO.HIGH)
            GPIO.output(_BOARD_PINS["right_bwd"], GPIO.HIGH)
            time.sleep(_TURN_90_SECS * degrees / 90)
            self.stop()

        def stop(self) -> None:
            for key in ("left_fwd", "left_bwd", "right_fwd", "right_bwd"):
                GPIO.output(_BOARD_PINS[key], GPIO.LOW)

        def collect(self) -> None:
            GPIO.output(_BOARD_PINS["collect"], GPIO.HIGH)
            time.sleep(1.0)
            GPIO.output(_BOARD_PINS["collect"], GPIO.LOW)

        def __del__(self) -> None:
            try:
                GPIO.cleanup()
            except Exception:
                pass

except ImportError:
    pass  # Jetson.GPIO only available on target hardware
