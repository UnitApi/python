#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI Read HCL Raw

This script simply reads the HCL file and prints its content.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to read HCL file"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI Read HCL Raw')
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
        # Read the HCL file
        with open(config_path, 'r') as f:
            hcl_content = f.read()
        
        # Print the content
        logger.info(f"Content of {config_path}:")
        print(hcl_content)
        
        logger.info("File read successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
