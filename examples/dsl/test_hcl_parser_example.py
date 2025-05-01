#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL HCL Parser Example

This script demonstrates how to use the HCL parser directly to parse and manipulate HCL configuration files.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.unitapi.dsl.parsers.hcl_parser import HCLParser
from src.unitapi.dsl.base import Extension, Device, Pipeline, PipelineStep

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to demonstrate HCL parser usage"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='UnitAPI DSL HCL Parser Example')
    parser.add_argument('--config', default='microphone_config.hcl', 
                        help='Path to the HCL configuration file (default: microphone_config.hcl)')
    parser.add_argument('--output', default=None, 
                        help='Path to save the modified configuration (default: <input>_modified.hcl)')
    args = parser.parse_args()
    
    # Resolve the configuration file path
    config_dir = Path(__file__).parent
    config_path = config_dir / args.config
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = config_path.with_stem(f"{config_path.stem}_modified").with_suffix('.hcl')
    
    try:
        # Create HCL parser
        hcl_parser = HCLParser()
        
        # Read and parse the HCL file
        logger.info(f"Reading configuration from {config_path}")
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Parse the configuration
        config = hcl_parser.parse(content)
        
        # Display the parsed configuration
        logger.info("Configuration parsed successfully")
        logger.info(f"Version: {config.get('version')}")
        logger.info(f"Extensions: {len(config.get('extensions', []))}")
        logger.info(f"Devices: {len(config.get('devices', []))}")
        logger.info(f"Pipelines: {len(config.get('pipelines', []))}")
        
        # Modify the configuration
        logger.info("Modifying the configuration...")
        
        # Add a new extension
        new_extension = Extension(
            type="extension",
            name="visualization",
            version=">=1.0.0",
            config={
                "enabled": True,
                "display_mode": "spectrum",
                # Use strings for color values to ensure proper HCL formatting
                "colors": ["red", "green", "blue"]
            }
        )
        config["extensions"].append(new_extension)
        
        # Add a new device
        new_device = Device(
            type="device",
            id="virtual-mic",
            device_type="virtual_microphone",
            capabilities=["recording", "streaming", "effects"],
            metadata={
                "location": "cloud",
                "model": "VirtualMic Pro"
            }
        )
        config["devices"].append(new_device)
        
        # Add a new pipeline
        new_pipeline = Pipeline(
            type="pipeline",
            name="audio-visualizer",
            source="virtual-mic",
            steps=[
                PipelineStep(
                    type="step",
                    action="capture",
                    params={
                        "sample_rate": 48000,
                        "channels": 2,
                        "buffer_size": 1024
                    }
                ),
                PipelineStep(
                    type="step",
                    action="visualize",
                    params={
                        "type": "spectrum",
                        "width": 800,
                        "height": 600,
                        # Use strings for color values to ensure proper HCL formatting
                        "colors": ["red", "green", "blue"]
                    }
                ),
                PipelineStep(
                    type="step",
                    action="display",
                    params={
                        "fullscreen": False,
                        "window_title": "Audio Visualizer"
                    }
                )
            ]
        )
        config["pipelines"].append(new_pipeline)
        
        # Convert the modified configuration back to HCL
        modified_hcl = hcl_parser.to_string(config)
        
        # Save the modified configuration
        logger.info(f"Saving modified configuration to {output_path}")
        with open(output_path, 'w') as f:
            f.write(modified_hcl)
        
        # Validate the modified configuration
        is_valid = hcl_parser.validate(config)
        logger.info(f"Modified configuration is {'valid' if is_valid else 'invalid'}")
        
        # Parse the modified configuration to ensure it's valid
        with open(output_path, 'r') as f:
            modified_content = f.read()
        
        try:
            modified_config = hcl_parser.parse(modified_content)
            logger.info("Modified configuration parsed successfully")
            logger.info(f"Extensions: {len(modified_config.get('extensions', []))}")
            logger.info(f"Devices: {len(modified_config.get('devices', []))}")
            logger.info(f"Pipelines: {len(modified_config.get('pipelines', []))}")
            logger.info("Example completed successfully")
        except Exception as parse_error:
            logger.error(f"Error parsing modified configuration: {parse_error}")
            # Display the generated HCL for debugging
            logger.info("Generated HCL content:")
            logger.info(modified_hcl)
            raise
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
