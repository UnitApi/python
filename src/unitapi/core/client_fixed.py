"""
UnitAPI Client implementation with WebSocket support.
"""

import logging
import json
import asyncio
import websockets
from typing import Dict, Any, Optional, List


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
        # WebSocket server is on port+1 as per device_discovery.py
        self.ws_port = server_port + 1
        self.ws_url = f"ws://{server_host}:{self.ws_port}"
        self.logger.debug(f"WebSocket URL: {self.ws_url}")

    async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to the server using WebSockets.

        Args:
            command: Command dictionary containing command name and parameters

        Returns:
            Dictionary containing the server's response
        """
        try:
            self.logger.debug(f"Connecting to WebSocket server at {self.ws_url}")
            async with websockets.connect(self.ws_url) as websocket:
                # Convert command to JSON
                command_json = json.dumps(command)
                self.logger.debug(f"Sending command: {command_json}")
                
                # Send command
                await websocket.send(command_json)
                
                # Wait for response
                response_json = await websocket.recv()
                self.logger.debug(f"Received response: {response_json}")
                
                # Parse response
                response = json.loads(response_json)
                return response
        except Exception as e:
            self.logger.error(f"WebSocket communication error: {e}")
            return {"status": "error", "message": f"Communication error: {str(e)}"}

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
            self.logger.error(f"Failed to list devices: {error_msg}")
            return []

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
            "action": "register_device",
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

        cmd = {
            "action": "execute_command",
            "device_id": device_id,
            "command": command,
            "params": params or {}
        }
        
        return await self.send_command(cmd)
