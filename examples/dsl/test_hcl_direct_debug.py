#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI HCL Direct Test (Debug Version)

This script uses the Python HCL library directly to parse the HCL file and prints the structure of the parsed data.
"""

import os
import sys
import logging
import json
from pathlib import Path
import pprint

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to parse HCL file directly"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI HCL Direct Test (Debug Version)')
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
        # Try to import the hcl library
        try:
            import hcl
            logger.info("Successfully imported HCL library")
        except ImportError:
            logger.error("HCL library not found. Installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-hcl2"])
            import hcl
            logger.info("HCL library installed successfully")
        
        # Read and parse the HCL file
        with open(config_path, 'r') as f:
            try:
                # Try using python-hcl2
                import hcl2
                data = hcl2.load(f)
                logger.info("Parsed using python-hcl2")
            except (ImportError, NameError):
                # Fall back to python-hcl
                f.seek(0)  # Reset file pointer
                data = hcl.load(f)
                logger.info("Parsed using python-hcl")
        
        # Print the structure of the parsed data
        logger.info("Structure of parsed data:")
        logger.info(pprint.pformat(data))
        
        # Print the type of each top-level key
        logger.info("Types of top-level keys:")
        for key, value in data.items():
            logger.info(f"  - {key}: {type(value)}")
        
        # Check if 'extension' is a list or a dictionary
        if 'extension' in data:
            logger.info(f"Type of 'extension': {type(data['extension'])}")
            if isinstance(data['extension'], list):
                logger.info("'extension' is a list with the following items:")
                for i, item in enumerate(data['extension']):
                    logger.info(f"  - Item {i}: {type(item)}")
                    logger.info(f"    Content: {item}")
            elif isinstance(data['extension'], dict):
                logger.info("'extension' is a dictionary with the following keys:")
                for key, value in data['extension'].items():
                    logger.info(f"  - {key}: {type(value)}")
        
        # Save the parsed configuration as JSON for reference
        output_path = config_path.with_suffix('.json')
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved parsed configuration to {output_path}")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
