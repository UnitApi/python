"""
UnitAPI Client implementation.
"""

import logging
from typing import Dict, Any, Optional, List
import asyncio


class UnitAPIClient:
    """
    UnitAPI Client class for interacting with the UnitAPI server.
    """

    def __init__(self, server_host: str, server_port: int):
        """
        Initialize the UnitAPI client.

        Args:
            server_host: Server hostname or IP address
            server_port: Server port number
        """
        self.host = server_host
        self.port = server_port
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to the server.

        Args:
            command: Command dictionary containing command name and parameters

        Returns:
            Dictionary containing the server's response
        """
        # In a real implementation, this would use websockets or HTTP
        # For now, we'll just return a mock response for testing

        # If the command is list_devices, return a mock list of devices
        if command.get("action") == "list_devices":
            return {
                "status": "success",
                "devices": [
                    {
                        "device_id": "speaker_rpi",
                        "name": "Raspberry Pi Speaker",
                        "type": "speaker",
                        "metadata": {
                            "speaker_type": "raspberry_pi",
                            "virtual": True,
                            "sample_rate": 44100,
                            "channels": 2,
                        },
                    }
                ],
            }

        return {"status": "success", "data": {"message": "Command processed"}}

    async def list_devices(self, device_type=None):
        """
        List all devices registered with the server.

        Args:
            device_type (str, optional): Filter devices by type

        Returns:
            list: List of device information dictionaries
        """
        command = {
            "action": "list_devices",
        }

        if device_type:
            command["device_type"] = device_type

        response = await self.send_command(command)

        if response.get("status") == "success":
            return response.get("devices", [])
        else:
            # Handle error case
            error_msg = response.get("message", "Unknown error")
            raise Exception(f"Failed to list devices: {error_msg}")

    async def register_device(
        self,
        device_id: str,
        device_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a new device with the server.

        Args:
            device_id: Unique identifier for the device
            device_type: Type of device (e.g., 'sensor', 'camera')
            metadata: Optional device metadata

        Returns:
            Dictionary containing registration status
        """
        command = {
            "command": "register_device",
            "device_id": device_id,
            "device_type": device_type,
            "metadata": metadata or {},
        }
        return await self.send_command(command)

    async def execute_command(
        self, device_id: str, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on a device.

        Args:
            device_id: ID of the device to control
            command: Command to execute
            params: Optional command parameters

        Returns:
            Dictionary containing the command result
        """
        self.logger.info(f"Executing command '{command}' on device '{device_id}'")

        # In a real implementation, this would send the command to the server
        # For now, we'll return mock responses based on the command

        if device_id == "speaker_rpi":
            # Handle speaker commands
            if command == "play_audio":
                # Simulate audio playback
                playback_id = f"play_{asyncio.get_event_loop().time()}"
                return {
                    "status": "success",
                    "playback_id": playback_id,
                    "start_time": asyncio.get_event_loop().time(),
                    "audio_file": params.get("audio_file", ""),
                }
            elif command == "stop_playback":
                # Simulate stopping playback
                return {
                    "status": "success",
                    "playback_id": params.get("playback_id", ""),
                    "duration": 1.5,  # Mock duration
                }
            elif command == "set_volume":
                # Simulate setting volume
                return {
                    "status": "success",
                    "volume": params.get("volume", 0.8),
                }
            elif command == "get_volume":
                # Simulate getting volume
                return {
                    "status": "success",
                    "volume": 0.8,  # Mock volume
                }
            else:
                # Generic speaker command response
                return {
                    "status": "success",
                    "message": f"Command '{command}' executed on {device_id}",
                    "params": params or {},
                }
        elif "thermostat" in device_id:
            # Simulate thermostat response
            if command == "status":
                return {
                    "status": "online",
                    "temperature": 22.5,
                    "target": 23.0,
                    "mode": "heat",
                }
            elif command == "set_temperature":
                # Simulate thermostat temperature setting
                temperature = params.get("temperature", 22)
                return {
                    "status": "success",
                    "message": f"Temperature set to {temperature}°C",
                    "temperature": temperature,
                }
            else:
                return {"status": "success", "message": "Command executed"}
        elif "light" in device_id:
            # Simulate light response
            if command == "status":
                return {
                    "status": "online",
                    "power": "on",
                    "brightness": 80,
                    "color": "warm_white",
                }
            elif command == "toggle":
                # Simulate light toggling
                return {"status": "success", "power": "on", "message": "Device toggled"}
            else:
                return {"status": "success", "message": "Command executed"}
        else:
            # Generic command response
            return {
                "status": "success",
                "message": f"Command '{command}' executed on {device_id}",
                "params": params or {},
            }
