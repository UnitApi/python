#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL HCL Parser Direct Test

This script demonstrates how to use the HCL parser directly with a simple configuration.
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
    # Create a simple configuration
    config = {
        "version": "1.0",
        "extensions": [
            Extension(
                type="extension",
                name="test_extension",
                version="1.0.0",
                config={
                    "enabled": True,
                    "mode": "test"
                }
            )
        ],
        "devices": [
            Device(
                type="device",
                id="test_device",
                device_type="test_type",
                capabilities=["test1", "test2"],
                metadata={
                    "location": "test_location",
                    "active": True
                }
            )
        ],
        "pipelines": [
            Pipeline(
                type="pipeline",
                name="test_pipeline",
                source="test_device",
                steps=[
                    PipelineStep(
                        type="step",
                        action="test_step",
                        params={
                            "param1": "value1",
                            "param2": 123,
                            "param3": True,
                            "param4": ["item1", "item2"]
                        }
                    )
                ]
            )
        ]
    }
    
    try:
        # Create HCL parser
        hcl_parser = HCLParser()
        
        # Convert the configuration to HCL
        hcl_content = hcl_parser.to_string(config)
        
        # Display the generated HCL
        logger.info("Generated HCL content:")
        logger.info(hcl_content)
        
        # Save the HCL to a file
        output_path = Path(__file__).parent / "test_config.hcl"
        with open(output_path, 'w') as f:
            f.write(hcl_content)
        logger.info(f"Saved HCL to {output_path}")
        
        # Parse the HCL back to a configuration
        with open(output_path, 'r') as f:
            content = f.read()
        
        parsed_config = hcl_parser.parse(content)
        
        # Display the parsed configuration
        logger.info("Parsed configuration:")
        logger.info(f"Version: {parsed_config.get('version')}")
        logger.info(f"Extensions: {len(parsed_config.get('extensions', []))}")
        logger.info(f"Devices: {len(parsed_config.get('devices', []))}")
        logger.info(f"Pipelines: {len(parsed_config.get('pipelines', []))}")
        
        # Verify the parsed configuration
        extension = parsed_config["extensions"][0]
        logger.info(f"Extension name: {extension.name}")
        logger.info(f"Extension version: {extension.version}")
        logger.info(f"Extension config: {extension.config}")
        
        device = parsed_config["devices"][0]
        logger.info(f"Device ID: {device.id}")
        logger.info(f"Device type: {device.device_type}")
        logger.info(f"Device capabilities: {device.capabilities}")
        logger.info(f"Device metadata: {device.metadata}")
        
        pipeline = parsed_config["pipelines"][0]
        logger.info(f"Pipeline name: {pipeline.name}")
        logger.info(f"Pipeline source: {pipeline.source}")
        logger.info(f"Pipeline steps: {len(pipeline.steps)}")
        
        step = pipeline.steps[0]
        logger.info(f"Step action: {step.action}")
        logger.info(f"Step params: {step.params}")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
