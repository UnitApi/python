#!/usr/bin/env python3
"""
Raspberry Pi GPIO Server Example

This script demonstrates how to create a UnitAPI server that exposes GPIO functionality
on a Raspberry Pi. This server can be used with the gpio_control.py client example.
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.devices.gpio import GPIODevice


class RPiGPIOServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi GPIO server.

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
        
        # GPIO Device
        self.gpio_device = None
        
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
        if self.gpio_device:
            try:
                await self.gpio_device.disconnect()
                self.logger.info("GPIO device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting GPIO device: {e}")

    async def setup_gpio_device(self):
        """
        Set up and register the GPIO device.

        Returns:
            Success status
        """
        try:
            # Create GPIO device
            self.gpio_device = GPIODevice(
                device_id="gpio_rpi",
                name="Raspberry Pi GPIO",
                metadata={"platform": "raspberry_pi"}
            )
            
            # Connect the device
            await self.gpio_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.gpio_device.device_id,
                device_type=self.gpio_device.type,
                metadata=self.gpio_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.gpio_device.device_id,
                command="set_pin_mode",
                handler=self.gpio_device.execute_command
            )
            
            self.server.register_command_handler(
                device_id=self.gpio_device.device_id,
                command="digital_write",
                handler=self.gpio_device.execute_command
            )
            
            self.server.register_command_handler(
                device_id=self.gpio_device.device_id,
                command="digital_read",
                handler=self.gpio_device.execute_command
            )
            
            self.server.register_command_handler(
                device_id=self.gpio_device.device_id,
                command="pwm_write",
                handler=self.gpio_device.execute_command
            )
            
            self.logger.info(f"GPIO device registered: {self.gpio_device.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up GPIO device: {e}")
            return False

    async def start(self):
        """
        Start the GPIO server.
        """
        try:
            # Set up GPIO device
            if not await self.setup_gpio_device():
                self.logger.error("Failed to set up GPIO device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi GPIO Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi GPIO server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi GPIO Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    server = RPiGPIOServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
