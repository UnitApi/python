#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI HCL Direct Test

This script uses the Python HCL library directly to parse the HCL file.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to parse HCL file directly"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI HCL Direct Test')
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
                config = hcl2.load(f)
                logger.info("Parsed using python-hcl2")
            except (ImportError, NameError):
                # Fall back to python-hcl
                f.seek(0)  # Reset file pointer
                config = hcl.load(f)
                logger.info("Parsed using python-hcl")
        
        # Display the parsed configuration
        logger.info("Configuration parsed successfully")
        logger.info(f"Version: {config.get('version')}")
        
        # Print extensions
        extensions = config.get('extension', {})
        logger.info(f"Extensions: {len(extensions)}")
        for name, ext in extensions.items():
            logger.info(f"  - {name} (version: {ext.get('version')})")
            logger.info(f"    Config: {ext.get('config', {})}")
        
        # Print devices
        devices = config.get('device', {})
        logger.info(f"Devices: {len(devices)}")
        for name, dev in devices.items():
            logger.info(f"  - {name} (type: {dev.get('type')})")
            logger.info(f"    Capabilities: {dev.get('capabilities', [])}")
            logger.info(f"    Metadata: {dev.get('metadata', {})}")
        
        # Print pipelines
        pipelines = config.get('pipeline', {})
        logger.info(f"Pipelines: {len(pipelines)}")
        for name, pipeline in pipelines.items():
            logger.info(f"  - {name} (source: {pipeline.get('source')})")
            steps = pipeline.get('step', {})
            logger.info(f"    Steps: {len(steps)}")
            for step_name, step in steps.items():
                logger.info(f"      - {step_name}: {step}")
        
        # Save the parsed configuration as JSON for reference
        output_path = config_path.with_suffix('.json')
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved parsed configuration to {output_path}")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
