"""
UnitAPI Server implementation.
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any


class UnitAPIServer:
    """
    UnitAPI Server class for managing device registration and communication.
    """

    def __init__(self, host: str, port: int):
        """
        Initialize the UnitAPI server.

        Args:
            host: Server hostname or IP address
            port: Server port number
        """
        self.host = host
        self.port = port
        self._devices: Dict[str, Dict] = {}
        self._command_handlers: Dict[str, Dict[str, Callable]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_device(self, device_id: str, device_type: str, metadata: Dict) -> None:
        """
        Register a new device with the server.

        Args:
            device_id: Unique identifier for the device
            device_type: Type of device (e.g., 'sensor', 'camera')
            metadata: Additional device information

        Raises:
            ValueError: If device_id is already registered
        """
        if device_id in self._devices:
            raise ValueError(f"Device with ID '{device_id}' is already registered")

        self._devices[device_id] = {"type": device_type, "metadata": metadata}

    def list_devices(self, device_type: Optional[str] = None) -> Dict[str, Dict]:
        """
        List registered devices, optionally filtered by type.

        Args:
            device_type: Optional filter for device type

        Returns:
            Dictionary of devices matching the filter criteria
        """
        if device_type is None:
            return self._devices.copy()

        return {
            device_id: device_info
            for device_id, device_info in self._devices.items()
            if device_info["type"] == device_type
        }

    def register_command_handler(
        self, device_id: str, command: str, handler: Callable
    ) -> None:
        """
        Register a command handler for a specific device.

        Args:
            device_id: The device ID to register the command handler for
            command: The command name
            handler: The function to handle the command

        Raises:
            ValueError: If the device is not registered
        """
        if device_id not in self._devices:
            raise ValueError(f"Device with ID '{device_id}' is not registered")

        if device_id not in self._command_handlers:
            self._command_handlers[device_id] = {}

        self._command_handlers[device_id][command] = handler
        self.logger.debug(
            f"Registered command handler for '{command}' on device '{device_id}'"
        )

    async def start(self) -> None:
        """
        Start the UnitAPI server.

        This method starts the server and keeps it running until stopped.
        """
        self.logger.info(f"Starting UnitAPI server on {self.host}:{self.port}")

        # In a real implementation, this would start a server
        # For now, we'll just simulate a running server
        while True:
            await asyncio.sleep(1)
