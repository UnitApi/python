#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL Multi-Format Configuration Test

This script demonstrates how to load, validate, and execute configurations in multiple formats,
as well as how to combine configurations from different formats.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from unitapi import UnitAPI
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.validators.schema import validate_config_with_details
from unitapi.dsl.runtime.executor import DSLExecutor
from unitapi.dsl.runtime.context import DSLContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_format_from_extension(file_path):
    """Get the format type from the file extension"""
    ext = Path(file_path).suffix.lower()
    if ext == '.yaml' or ext == '.yml':
        return 'yaml'
    elif ext == '.hcl':
        return 'hcl'
    elif ext == '.star':
        return 'star'
    elif ext == '.ua':
        return 'ua'
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

async def main():
    """Main function to test multi-format configurations"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI DSL Multi-Format Configuration Test')
    parser.add_argument('--base-config', default='camera_config.yaml', 
                        help='Path to the base configuration file')
    parser.add_argument('--device-config', default='microphone_config.hcl', 
                        help='Path to the device configuration file')
    parser.add_argument('--pipeline-config', default='speaker_config.star', 
                        help='Path to the pipeline configuration file')
    parser.add_argument('--additional-config', default='input_devices.ua', 
                        help='Path to an additional configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Validate without executing')
    parser.add_argument('--output-format', choices=['yaml', 'hcl', 'star', 'ua'], 
                        help='Output format for the combined configuration')
    args = parser.parse_args()
    
    # Resolve the configuration file paths
    config_dir = Path(__file__).parent
    base_config_path = config_dir / args.base_config
    device_config_path = config_dir / args.device_config
    pipeline_config_path = config_dir / args.pipeline_config
    additional_config_path = config_dir / args.additional_config
    
    # Check if all configuration files exist
    for path, name in [
        (base_config_path, "Base configuration"),
        (device_config_path, "Device configuration"),
        (pipeline_config_path, "Pipeline configuration"),
        (additional_config_path, "Additional configuration")
    ]:
        if not path.exists():
            logger.error(f"{name} file not found: {path}")
            sys.exit(1)
    
    try:
        # Load all configurations
        logger.info(f"Loading base configuration from {base_config_path}")
        base_config = ConfigLoader.load(str(base_config_path))
        
        logger.info(f"Loading device configuration from {device_config_path}")
        device_config = ConfigLoader.load(str(device_config_path))
        
        logger.info(f"Loading pipeline configuration from {pipeline_config_path}")
        pipeline_config = ConfigLoader.load(str(pipeline_config_path))
        
        logger.info(f"Loading additional configuration from {additional_config_path}")
        additional_config = ConfigLoader.load(str(additional_config_path))
        
        # Merge configurations
        logger.info("Merging configurations")
        
        # Create a combined configuration starting with the base
        combined_config = base_config.copy()
        
        # Add devices from all configurations
        all_devices = []
        all_devices.extend(base_config.get('devices', []))
        all_devices.extend(device_config.get('devices', []))
        all_devices.extend(pipeline_config.get('devices', []))
        all_devices.extend(additional_config.get('devices', []))
        
        # Ensure no duplicate device IDs
        device_ids = set()
        unique_devices = []
        for device in all_devices:
            if device.id not in device_ids:
                device_ids.add(device.id)
                unique_devices.append(device)
            else:
                logger.warning(f"Duplicate device ID found: {device.id}. Using first occurrence.")
        
        combined_config['devices'] = unique_devices
        
        # Add pipelines from all configurations
        all_pipelines = []
        all_pipelines.extend(base_config.get('pipelines', []))
        all_pipelines.extend(device_config.get('pipelines', []))
        all_pipelines.extend(pipeline_config.get('pipelines', []))
        all_pipelines.extend(additional_config.get('pipelines', []))
        
        # Ensure no duplicate pipeline names
        pipeline_names = set()
        unique_pipelines = []
        for pipeline in all_pipelines:
            if pipeline.name not in pipeline_names:
                pipeline_names.add(pipeline.name)
                unique_pipelines.append(pipeline)
            else:
                logger.warning(f"Duplicate pipeline name found: {pipeline.name}. Using first occurrence.")
        
        combined_config['pipelines'] = unique_pipelines
        
        # Add extensions from all configurations
        all_extensions = []
        all_extensions.extend(base_config.get('extensions', []))
        all_extensions.extend(device_config.get('extensions', []))
        all_extensions.extend(pipeline_config.get('extensions', []))
        all_extensions.extend(additional_config.get('extensions', []))
        
        # Ensure no duplicate extension names
        extension_names = set()
        unique_extensions = []
        for extension in all_extensions:
            if extension.name not in extension_names:
                extension_names.add(extension.name)
                unique_extensions.append(extension)
            else:
                logger.warning(f"Duplicate extension name found: {extension.name}. Using first occurrence.")
        
        combined_config['extensions'] = unique_extensions
        
        # Validate the combined configuration
        is_valid, error = validate_config_with_details(combined_config)
        if not is_valid:
            logger.error(f"Invalid combined configuration: {error}")
            sys.exit(1)
        
        logger.info("Combined configuration is valid")
        logger.info(f"Version: {combined_config.get('version')}")
        logger.info(f"Extensions: {len(combined_config.get('extensions', []))}")
        logger.info(f"Devices: {len(combined_config.get('devices', []))}")
        logger.info(f"Pipelines: {len(combined_config.get('pipelines', []))}")
        
        # Output the combined configuration if requested
        if args.output_format:
            output_format = args.output_format
            converted = ConfigLoader.convert(combined_config, output_format)
            output_path = config_dir / f"combined_config.{output_format}"
            with open(output_path, 'w') as f:
                f.write(converted)
            logger.info(f"Combined configuration written to {output_path}")
        
        if args.dry_run:
            logger.info("Dry run completed successfully")
            return
        
        # Initialize UnitAPI
        logger.info("Initializing UnitAPI")
        unitapi = UnitAPI()
        
        # Set up executor and context
        executor = DSLExecutor(unitapi)
        context = DSLContext()
        
        # Execute the combined configuration
        logger.info("Executing combined configuration")
        await executor.execute_config(combined_config)
        logger.info("Combined configuration executed successfully")
        
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
            await context.cleanup()
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
