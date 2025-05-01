#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL Example

This example demonstrates how to use the UnitAPI DSL module programmatically.
It loads a configuration file, validates it, and executes it.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.unitapi import UnitAPI
from src.unitapi.config.loader import ConfigLoader
from src.unitapi.dsl.validators.schema import validate_config_with_details
from src.unitapi.dsl.runtime.executor import DSLExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI DSL Example')
    parser.add_argument('config_file', help='Path to the configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Validate without executing')
    args = parser.parse_args()
    
    # Check if the configuration file exists
    config_path = Path(args.config_file)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {args.config_file}")
        sys.exit(1)
    
    try:
        # Load the configuration
        logger.info(f"Loading configuration from {args.config_file}")
        config = ConfigLoader.load(str(config_path))
        
        # Validate the configuration
        is_valid, error = validate_config_with_details(config)
        if not is_valid:
            logger.error(f"Invalid configuration: {error}")
            sys.exit(1)
        
        logger.info("Configuration is valid")
        logger.info(f"Version: {config.get('version')}")
        logger.info(f"Extensions: {len(config.get('extensions', []))}")
        logger.info(f"Devices: {len(config.get('devices', []))}")
        logger.info(f"Pipelines: {len(config.get('pipelines', []))}")
        
        if args.dry_run:
            logger.info("Dry run completed successfully")
            return
        
        # Initialize UnitAPI
        logger.info("Initializing UnitAPI")
        unitapi = UnitAPI()
        
        # Set up executor
        executor = DSLExecutor(unitapi)
        
        # Execute the configuration
        logger.info("Executing configuration")
        await executor.execute_config(config)
        logger.info("Configuration executed successfully")
        
        # Keep running until interrupted
        try:
            logger.info("Press Ctrl+C to stop")
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            # Clean up
            logger.info("Cleaning up")
            await executor.stop_all()
            await executor.cleanup()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
