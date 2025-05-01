#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL Starlark Configuration Test

This script demonstrates how to load, validate, and execute Starlark configuration files.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from unitapi.main import unitapi as UnitAPI
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.validators.schema import validate_config_with_details
from unitapi.dsl.runtime.executor import DSLExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to test Starlark configuration files"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI DSL Starlark Configuration Test')
    parser.add_argument('--config', default='example.star', 
                        help='Path to the Starlark configuration file (default: example.star)')
    parser.add_argument('--dry-run', action='store_true', help='Validate without executing')
    parser.add_argument('--convert-to', choices=['yaml', 'hcl', 'ua'], 
                        help='Convert the configuration to another format')
    parser.add_argument('--list-pipelines', action='store_true', 
                        help='List all pipelines in the configuration')
    args = parser.parse_args()
    
    # Resolve the configuration file path
    config_dir = Path(__file__).parent
    config_path = config_dir / args.config
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Load the configuration
        logger.info(f"Loading configuration from {config_path}")
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
        
        # List pipelines if requested
        if args.list_pipelines:
            logger.info("\nPipelines:")
            for pipeline in config.get('pipelines', []):
                logger.info(f"  - Name: {pipeline.name}")
                if hasattr(pipeline, 'source') and pipeline.source:
                    logger.info(f"    Source: {pipeline.source}")
                if hasattr(pipeline, 'target') and pipeline.target:
                    logger.info(f"    Target: {pipeline.target}")
                logger.info(f"    Steps: {len(pipeline.steps)}")
                logger.info("")
        
        # Convert to another format if requested
        if args.convert_to:
            converted = ConfigLoader.convert(config, args.convert_to)
            output_path = config_path.with_suffix(f".converted.{args.convert_to}")
            with open(output_path, 'w') as f:
                f.write(converted)
            logger.info(f"Converted configuration written to {output_path}")
            
            # Verify the converted configuration can be loaded back
            converted_config = ConfigLoader.load_from_string(converted, args.convert_to)
            logger.info("Converted configuration is valid")
        
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
