#!/usr/bin/env python3
"""
Remote Keyboard Server Example

This script runs on a Raspberry Pi to register a keyboard device with the UnitAPI server.
It allows remote clients to control the keyboard on the Raspberry Pi.
"""

import asyncio
import argparse
import logging
import os
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.devices import KeyboardDevice


class RemoteKeyboardServerExample:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize remote keyboard server example.

        Args:
            host: UnitAPI server host
            port: UnitAPI server port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI server
        self.server = UnitAPIServer(host=host, port=port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(
            host=host,
            port=port + 1
        )
        
        # Keyboard device
        self.keyboard = None

    async def start_server(self):
        """
        Start the UnitAPI server.
        """
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())

        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())
        
        self.logger.info(f"Server started on {self.server.host}:{self.server.port}")
        
        # Register keyboard device
        await self.register_keyboard()
        
        # Return tasks
        return [server_task, websocket_task]

    async def register_keyboard(self, device_id: str = "keyboard_01", name: str = "Raspberry Pi Keyboard"):
        """
        Register a keyboard device with the server.

        Args:
            device_id: Keyboard device ID
            name: Keyboard device name
        """
        try:
            # Create a keyboard device
            self.keyboard = KeyboardDevice(
                device_id=device_id,
                name=name,
                metadata={"layout": "us", "device_type": "raspberry_pi"}
            )
            
            # Connect to the keyboard
            await self.keyboard.connect()
            
            # Register with server
            self.server.register_device(
                device_id=self.keyboard.device_id,
                device_type='keyboard',
                metadata=self.keyboard.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.keyboard.device_id,
                command='type_text',
                handler=self.handle_type_text
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard.device_id,
                command='press_key',
                handler=self.handle_press_key
            )
            
            self.server.register_command_handler(
                device_id=self.keyboard.device_id,
                command='press_hotkey',
                handler=self.handle_press_hotkey
            )
            
            self.logger.info(f"Registered keyboard device: {name} (ID: {device_id})")
            
        except Exception as e:
            self.logger.error(f"Failed to register keyboard device: {e}")

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
                return {'error': 'No text provided'}
                
            self.logger.info(f"Typing text: '{text}'")
            await self.keyboard.type_text(text)
            
            return {'success': True, 'text': text}
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return {'error': str(e)}

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
                return {'error': 'No key provided'}
                
            self.logger.info(f"Pressing key: '{key}'")
            await self.keyboard.press_key(key)
            
            return {'success': True, 'key': key}
            
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return {'error': str(e)}

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
                return {'error': 'No keys provided'}
                
            key_str = '+'.join(keys)
            self.logger.info(f"Pressing hotkey: '{key_str}'")
            
            # Press all keys in sequence
            for key in keys:
                await self.keyboard.key_down(key)
                
            # Small delay
            await asyncio.sleep(0.1)
            
            # Release all keys in reverse order
            for key in reversed(keys):
                await self.keyboard.key_up(key)
            
            return {'success': True, 'hotkey': key_str}
            
        except Exception as e:
            self.logger.error(f"Error pressing hotkey: {e}")
            # Make sure all keys are released
            await self.keyboard.release_all_keys()
            return {'error': str(e)}


async def main():
    """
    Run the remote keyboard server example.
    """
    parser = argparse.ArgumentParser(description='Remote Keyboard Server Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    parser.add_argument('--device-id', default='keyboard_01', help='Keyboard device ID')
    parser.add_argument('--name', default='Raspberry Pi Keyboard', help='Keyboard device name')
    
    args = parser.parse_args()
    
    example = RemoteKeyboardServerExample(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # Start server
    tasks = await example.start_server()
    
    # Register keyboard with custom ID and name if provided
    if args.device_id != 'keyboard_01' or args.name != 'Raspberry Pi Keyboard':
        await example.register_keyboard(device_id=args.device_id, name=args.name)
    
    print(f"Remote Keyboard Server running on {args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    
    try:
        # Wait for server tasks
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
