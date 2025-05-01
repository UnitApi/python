#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI Client Test

This script demonstrates how to use the UnitAPIClient directly.
"""

import os
import sys
import asyncio
import logging

# Add the directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import directly from unitapi.core.client
from unitapi.core.client import UnitAPIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to test UnitAPIClient"""
    try:
        # Initialize UnitAPI client
        logger.info("Initializing UnitAPI client")
        client = UnitAPIClient(server_host='localhost', server_port=7890)
        
        # List available devices
        logger.info("Listing available devices")
        try:
            devices = await client.list_devices()
            logger.info(f"Found {len(devices)} device(s)")
            for i, device in enumerate(devices):
                logger.info(f"Device {i+1}: {device.get('name')} (ID: {device.get('device_id')})")
        except Exception as e:
            logger.warning(f"Failed to list devices: {e}")
            logger.info("This is expected if no UnitAPI server is running")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
