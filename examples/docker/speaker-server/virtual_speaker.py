#!/usr/bin/env python3
"""
UnitAPI Virtual Speaker Service

This script creates virtual speakers for testing the UnitAPI speaker agent.
It simulates multiple speakers on a system for testing purposes.
"""

import asyncio
import argparse
import logging
import os
import sys
import json
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VirtualSpeakerService")

# Import UnitAPI modules
try:
    from unitapi.core.server import UnitAPIServer
    from unitapi.protocols.websocket import WebSocketProtocol
    from unitapi.devices.remote_speaker_device import RemoteSpeakerDevice
except ImportError:
    logger.error("UnitAPI modules not found. Please install UnitAPI.")
    sys.exit(1)


class VirtualSpeakerService:
    """Service that creates and manages virtual speakers."""

    def __init__(
            self,
            num_speakers: int = 1,
            server_host: str = '0.0.0.0',
            server_port: int = 7890,
            ws_host: str = '0.0.0.0',
            ws_port: int = 8765
    ):
        """Initialize the virtual speaker service."""
        self.num_speakers = num_speakers
        self.server_host = server_host
        self.server_port = server_port
        self.ws_host = ws_host
        self.ws_port = ws_port
        
        # UnitAPI Server
        self.server = UnitAPIServer(host=server_host, port=server_port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(host=ws_host, port=ws_port)
        
        # Speakers registry
        self.speakers = {}
        
        logger.info(f"Virtual Speaker Service initialized with {num_speakers} speakers")

    async def create_virtual_speakers(self) -> None:
        """Create virtual speakers."""
        for i in range(self.num_speakers):
            device_id = f"virtual_speaker_{i+1}"
            name = f"Virtual Speaker {i+1}"
            location = f"Virtual Room {i+1}"
            
            # Create speaker metadata
            metadata = {
                "location": location,
                "sample_rate": 44100,
                "channels": 2,
                "virtual": True
            }
            
            # Create speaker device
            speaker = RemoteSpeakerDevice(
                device_id=device_id,
                name=name,
                metadata=metadata
            )
            
            # Connect speaker
            await speaker.connect()
            
            # Register in server
            self.server.register_device(
                device_id=device_id,
                device_type="speaker",
                metadata={
                    "name": name,
                    "location": location,
                    "virtual": True
                }
            )
            
            # Store in registry
            self.speakers[device_id] = speaker
            
            logger.info(f"Created virtual speaker: {name} (ID: {device_id})")

    async def start(self) -> None:
        """Start the virtual speaker service."""
        logger.info("Starting Virtual Speaker Service")
        
        # Create virtual speakers
        await self.create_virtual_speakers()
        
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())
        
        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())
        
        logger.info(f"Virtual Speaker Service running on {self.server_host}:{self.server_port}")
        logger.info(f"WebSocket server running on {self.ws_host}:{self.ws_port}")
        
        # Wait for servers to run
        await asyncio.gather(server_task, websocket_task)


async def main():
    """Run the virtual speaker service."""
    parser = argparse.ArgumentParser(description="UnitAPI Virtual Speaker Service")
    parser.add_argument("--num-speakers", type=int, default=1, help="Number of virtual speakers to create")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=7890, help="Server port")
    parser.add_argument("--ws-host", default="0.0.0.0", help="WebSocket host")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket port")
    
    args = parser.parse_args()
    
    # Create virtual speaker service
    service = VirtualSpeakerService(
        num_speakers=args.num_speakers,
        server_host=args.host,
        server_port=args.port,
        ws_host=args.ws_host,
        ws_port=args.ws_port
    )
    
    # Start the service
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Virtual Speaker Service stopped by user")
    except Exception as e:
        logger.error(f"Virtual Speaker Service error: {e}")
        sys.exit(1)
