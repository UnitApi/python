#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI HCL Parser Direct Test

This script demonstrates how to use the HCL parser directly without going through the DSL module.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the HCL parser directly
import importlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to test HCL parser directly"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI HCL Parser Direct Test')
    parser.add_argument('--config', default='microphone_config.hcl', 
                        help='Path to the HCL configuration file (default: microphone_config.hcl)')
    args = parser.parse_args()
    
    # Resolve the configuration file path
    config_dir = Path(__file__).parent
    config_path = config_dir / args.config
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    try:
        # Import the HCL parser directly
        try:
            hcl_parser_module = importlib.import_module('unitapi.dsl.parsers.hcl_parser')
            HCLParser = getattr(hcl_parser_module, 'HCLParser')
            logger.info("Successfully imported HCL parser")
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import HCL parser: {e}")
            sys.exit(1)
        
        # Read the HCL file
        with open(config_path, 'r') as f:
            hcl_content = f.read()
        
        # Parse the HCL content
        parser = HCLParser()
        config = parser.parse(hcl_content)
        
        # Display basic configuration info
        logger.info("Configuration parsed successfully")
        logger.info(f"Raw config: {config}")
        
        # Display basic configuration info
        logger.info(f"Version: {config.get('version')}")
        logger.info(f"Extensions: {len(config.get('extensions', []))}")
        logger.info(f"Devices: {len(config.get('devices', []))}")
        logger.info(f"Pipelines: {len(config.get('pipelines', []))}")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
