"""
UnitAPI device implementations.
"""

from .base import (
    DeviceStatus,
    BaseDevice,
    SensorDevice,
    AudioDevice,
    GPIODevice,
    InputDevice,
)
from .camera import CameraDevice
from .microphone import MicrophoneDevice
from .gpio import GPIODevice
from .remote_speaker_device import RemoteSpeakerDevice
from .mouse import MouseDevice
from .keyboard import KeyboardDevice
from .touchscreen import TouchscreenDevice
from .gamepad import GamepadDevice

__all__ = [
    # Base classes
    "DeviceStatus",
    "BaseDevice",
    "SensorDevice",
    "AudioDevice",
    "GPIODevice",
    "InputDevice",
    
    # Device implementations
    "CameraDevice",
    "MicrophoneDevice",
    "GPIODevice",
    "RemoteSpeakerDevice",
    "MouseDevice",
    "KeyboardDevice",
    "TouchscreenDevice",
    "GamepadDevice",
]
