"""
Base device classes for UnitAPI.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple


class DeviceStatus(Enum):
    """Device connection status."""

    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    ERROR = "ERROR"
    BUSY = "BUSY"


class BaseDevice(ABC):
    """Base class for all UnitAPI devices."""

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base device.

        Args:
            device_id: Unique identifier for the device
            name: Human-readable device name
            device_type: Type of device
            metadata: Optional device metadata
        """
        self.device_id = device_id
        self.name = name
        self.type = device_type
        self.metadata = metadata or {}
        self.status = DeviceStatus.OFFLINE

    async def connect(self) -> bool:
        """
        Connect to the device.

        Returns:
            bool: True if connection successful
        """
        self.status = DeviceStatus.ONLINE
        return True

    async def disconnect(self) -> bool:
        """
        Disconnect from the device.

        Returns:
            bool: True if disconnection successful
        """
        self.status = DeviceStatus.OFFLINE
        return True

    async def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a device-specific command.

        Args:
            command: Command to execute
            params: Optional command parameters

        Returns:
            Dictionary containing command execution results
        """
        raise NotImplementedError("Device must implement execute_command")


class SensorDevice(BaseDevice):
    """Base class for sensor devices."""

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str = "sensor",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize sensor device."""
        super().__init__(device_id, name, device_type, metadata)

    async def read_sensor(self) -> Dict[str, Any]:
        """
        Read sensor data.

        Returns:
            Dictionary containing sensor readings
        """
        return {"device_id": self.device_id, "timestamp": None, "value": None}


class AudioDevice(BaseDevice):
    """Base class for audio devices."""

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str = "audio",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize audio device."""
        super().__init__(device_id, name, device_type, metadata)

    async def get_audio_config(self) -> Dict[str, Any]:
        """
        Get audio device configuration.

        Returns:
            Dictionary containing audio configuration
        """
        return {
            "sample_rate": self.metadata.get("sample_rate", 44100),
            "channels": self.metadata.get("channels", 2),
            "format": self.metadata.get("format", "PCM_16"),
        }


class GPIODevice(BaseDevice):
    """Base class for GPIO devices."""

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str = "gpio",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize GPIO device."""
        super().__init__(device_id, name, device_type, metadata)
        self._pin_modes = {}

    async def set_pin_mode(self, pin: int, mode: str) -> Dict[str, Any]:
        """
        Set GPIO pin mode.

        Args:
            pin: Pin number
            mode: Pin mode ('input' or 'output')

        Returns:
            Dictionary containing operation status
        """
        self._pin_modes[pin] = mode
        return {"status": "success", "pin": pin, "mode": mode}

    async def digital_write(self, pin: int, value: bool) -> Dict[str, Any]:
        """
        Write digital value to GPIO pin.

        Args:
            pin: Pin number
            value: Digital value to write

        Returns:
            Dictionary containing operation status
        """
        return {"status": "success", "pin": pin, "value": value}

    async def digital_read(self, pin: int) -> Dict[str, Any]:
        """
        Read digital value from GPIO pin.

        Args:
            pin: Pin number

        Returns:
            Dictionary containing pin value
        """
        return {"status": "success", "pin": pin, "value": False}


class InputDevice(BaseDevice):
    """Base class for input devices like mouse, keyboard, etc."""

    def __init__(
        self,
        device_id: str,
        name: str,
        device_type: str = "input",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize input device."""
        super().__init__(device_id, name, device_type, metadata)
        self._event_listeners = []

    async def send_input(
        self, input_type: str, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send input to the device.

        Args:
            input_type: Type of input (e.g., 'click', 'key_press')
            input_data: Input data specific to the input type

        Returns:
            Dictionary containing operation status
        """
        return {
            "status": "success",
            "device_id": self.device_id,
            "input_type": input_type,
            "input_data": input_data,
        }

    async def register_event_listener(self, callback) -> Dict[str, Any]:
        """
        Register a callback function to receive input events.

        Args:
            callback: Async function to call when an input event occurs

        Returns:
            Dictionary containing registration status
        """
        self._event_listeners.append(callback)
        return {
            "status": "success",
            "device_id": self.device_id,
            "listener_id": len(self._event_listeners) - 1,
        }

    async def unregister_event_listener(self, listener_id: int) -> Dict[str, Any]:
        """
        Unregister an event listener.

        Args:
            listener_id: ID of the listener to unregister

        Returns:
            Dictionary containing unregistration status
        """
        if 0 <= listener_id < len(self._event_listeners):
            self._event_listeners.pop(listener_id)
            return {"status": "success", "device_id": self.device_id}
        return {"status": "error", "message": "Invalid listener ID"}
