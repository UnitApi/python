#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL HCL Configuration Test (Simplified)

This script demonstrates how to load and validate HCL configuration files.
"""

import os
import sys
import logging
from pathlib import Path

# Add the directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import directly from unitapi.config.loader
from unitapi.config.loader import ConfigLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to test HCL configuration files"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI DSL HCL Configuration Test (Simplified)')
    parser.add_argument('--config', default='microphone_config.hcl', 
                        help='Path to the HCL configuration file (default: microphone_config.hcl)')
    parser.add_argument('--convert-to', choices=['yaml', 'star', 'ua'], 
                        help='Convert the configuration to another format')
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
        
        # Display basic configuration info
        logger.info("Configuration loaded successfully")
        logger.info(f"Version: {config.get('version')}")
        logger.info(f"Extensions: {len(config.get('extensions', []))}")
        logger.info(f"Devices: {len(config.get('devices', []))}")
        logger.info(f"Pipelines: {len(config.get('pipelines', []))}")
        
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
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
