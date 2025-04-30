#!/usr/bin/env python3
"""
PC Mouse Server Example

This script runs on a PC to register a mouse device with the UnitAPI server.
It allows remote clients to control the mouse on the PC.
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Dict, Any, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.devices import MouseDevice


class PCMouseServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize PC Mouse server.

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
        
        # Mouse Device
        self.mouse_device = None
        
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
        if self.mouse_device:
            try:
                await self.mouse_device.disconnect()
                self.logger.info("Mouse device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting mouse device: {e}")

    async def setup_mouse_device(self, device_id: str = "mouse_01", name: str = "PC Mouse"):
        """
        Set up and register the mouse device.

        Args:
            device_id: Mouse device ID
            name: Mouse device name

        Returns:
            Success status
        """
        try:
            # Create mouse device
            self.mouse_device = MouseDevice(
                device_id=device_id,
                name=name,
                metadata={"type": "optical", "device_type": "pc"}
            )
            
            # Connect the device
            await self.mouse_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.mouse_device.device_id,
                device_type=self.mouse_device.type,
                metadata=self.mouse_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="move_to",
                handler=self.handle_move_to
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="move_relative",
                handler=self.handle_move_relative
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="click",
                handler=self.handle_click
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="double_click",
                handler=self.handle_double_click
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="button_down",
                handler=self.handle_button_down
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="button_up",
                handler=self.handle_button_up
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="scroll",
                handler=self.handle_scroll
            )
            
            self.server.register_command_handler(
                device_id=self.mouse_device.device_id,
                command="drag",
                handler=self.handle_drag
            )
            
            self.logger.info(f"Mouse device registered: {name} (ID: {device_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up mouse device: {e}")
            return False

    async def handle_move_to(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle move_to command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            x = params.get('x', 0)
            y = params.get('y', 0)
            
            self.logger.info(f"Moving mouse to position ({x}, {y})")
            result = await self.mouse_device.move_to(x, y)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_move_relative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle move_relative command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            dx = params.get('dx', 0)
            dy = params.get('dy', 0)
            
            self.logger.info(f"Moving mouse by ({dx}, {dy})")
            result = await self.mouse_device.move_relative(dx, dy)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error moving mouse relatively: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle click command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            button = params.get('button', 'left')
            
            self.logger.info(f"Clicking {button} mouse button")
            result = await self.mouse_device.click(button)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error clicking mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_double_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle double_click command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            button = params.get('button', 'left')
            
            self.logger.info(f"Double-clicking {button} mouse button")
            result = await self.mouse_device.double_click(button)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error double-clicking mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_button_down(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle button_down command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            button = params.get('button', 'left')
            
            self.logger.info(f"Pressing {button} mouse button down")
            result = await self.mouse_device.button_down(button)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error pressing mouse button down: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_button_up(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle button_up command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            button = params.get('button', 'left')
            
            self.logger.info(f"Releasing {button} mouse button")
            result = await self.mouse_device.button_up(button)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error releasing mouse button: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle scroll command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            amount = params.get('amount', 0)
            
            direction = "up" if amount > 0 else "down"
            self.logger.info(f"Scrolling {direction} by {abs(amount)}")
            result = await self.mouse_device.scroll(amount)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error scrolling mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def handle_drag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle drag command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        try:
            x = params.get('x', 0)
            y = params.get('y', 0)
            button = params.get('button', 'left')
            
            self.logger.info(f"Dragging with {button} button to position ({x}, {y})")
            result = await self.mouse_device.drag(x, y, button)
            
            return {**result, 'status': 'success'}
            
        except Exception as e:
            self.logger.error(f"Error dragging mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def start(self):
        """
        Start the mouse server.
        """
        try:
            # Set up mouse device
            if not await self.setup_mouse_device():
                self.logger.error("Failed to set up mouse device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"PC Mouse Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the PC Mouse server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI PC Mouse Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    parser.add_argument('--device-id', default='mouse_01', help='Mouse device ID')
    parser.add_argument('--name', default='PC Mouse', help='Mouse device name')
    
    args = parser.parse_args()
    
    server = PCMouseServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # Start server with custom device ID and name if provided
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
