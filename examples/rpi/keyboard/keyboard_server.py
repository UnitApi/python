#!/usr/bin/env python3
"""
Raspberry Pi Keyboard Server Example

This script runs on a Raspberry Pi to register a keyboard device with the UnitAPI server.
It allows remote clients to control the keyboard on the Raspberry Pi.
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Dict, Any, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.devices import KeyboardDevice


class RPiKeyboardServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Keyboard server.

        Args:
            host: Server host address
            port: Server port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI Server
        self.server = UnitAPIServer(host=host, port=port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(
            host=host,
            port=port + 1
        )
        
        # Keyboard Device
        self.keyboard_device = None
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        self.logger.info("Shutdown signal received, cleaning up...")
        
        # Create a new event loop for cleanup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run cleanup
            loop.run_until_complete(self._cleanup())
        finally:
            loop.close()
            sys.exit(0)

    async def _cleanup(self):
        """Clean up resources before shutdown."""
        if self.keyboard_device:
            try:
                # Release all keys before disconnecting
                await self.keyboard_device.release_all_keys()
                await self.keyboard_device.disconnect()
                self.logger.info("Keyboard device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting keyboard device: {e}")

    async def setup_keyboard_device(self, device_id: str = "keyboard_rpi", name: str = "Raspberry Pi Keyboard"):
        """
        Set up and register the keyboard device.

        Args:
            device_id: Keyboard device ID
            name: Keyboard device name

        Returns:
            Success status
        """
        try:
            # Create keyboard device
            self.keyboard_device = KeyboardDevice(
                device_id=device_id,
                name=name,
                metadata={"layout": "us", "device_type": "raspberry_pi"}
            )
            
            # Connect the device
            await self.keyboard_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.keyboard_device.device_id,
                device_type=self.keyboard_device.type,
                metadata=self.keyboard_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="key_down",
                handler=self.handle_key_down
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="key_up",
                handler=self.handle_key_up
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="press_key",
                handler=self.handle_press_key
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="type_text",
                handler=self.handle_type_text
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="press_hotkey",
                handler=self.handle_press_hotkey
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard_device.device_id,
                command="release_all_keys",
                handler=self.handle_release_all_keys
            )
            
            self.logger.info(f"Keyboard device registered: {name} (ID: {device_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up keyboard device: {e}")
            return False

    async def handle_key_down(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle key_down command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            key = params.get('key', '')
            
            if not key:
                return {'error': 'No key provided', 'status': 'error'}
                
            self.logger.info(f"Pressing key down: '{key}'")
            result = await self.keyboard_device.key_down(key)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error pressing key down: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_key_up(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle key_up command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            key = params.get('key', '')
            
            if not key:
                return {'error': 'No key provided', 'status': 'error'}
                
            self.logger.info(f"Releasing key: '{key}'")
            result = await self.keyboard_device.key_up(key)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error releasing key: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_press_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle press_key command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            key = params.get('key', '')
            
            if not key:
                return {'error': 'No key provided', 'status': 'error'}
                
            self.logger.info(f"Pressing key: '{key}'")
            result = await self.keyboard_device.press_key(key)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle type_text command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            text = params.get('text', '')
            
            if not text:
                return {'error': 'No text provided', 'status': 'error'}
                
            self.logger.info(f"Typing text: '{text}'")
            result = await self.keyboard_device.type_text(text)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_press_hotkey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle press_hotkey command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            keys = params.get('keys', [])
            
            if not keys:
                return {'error': 'No keys provided', 'status': 'error'}
                
            key_str = '+'.join(keys)
            self.logger.info(f"Pressing hotkey: '{key_str}'")
            
            result = await self.keyboard_device.press_hotkey(*keys)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error pressing hotkey: {e}")
            # Make sure all keys are released
            await self.keyboard_device.release_all_keys()
            return {'error': str(e), 'status': 'error'}

    async def handle_release_all_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle release_all_keys command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            self.logger.info("Releasing all keys")
            result = await self.keyboard_device.release_all_keys()
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error releasing all keys: {e}")
            return {'error': str(e), 'status': 'error'}

    async def start(self):
        """
        Start the keyboard server.
        """
        try:
            # Set up keyboard device
            if not await self.setup_keyboard_device():
                self.logger.error("Failed to set up keyboard device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi Keyboard Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi Keyboard server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Keyboard Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    parser.add_argument('--device-id', default='keyboard_rpi', help='Keyboard device ID')
    parser.add_argument('--name', default='Raspberry Pi Keyboard', help='Keyboard device name')
    
    args = parser.parse_args()
    
    server = RPiKeyboardServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # Start server with custom device ID and name if provided
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
