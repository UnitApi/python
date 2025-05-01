#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UnitAPI DSL HCL Configuration Test (Simplified) - Fixed Version

This script demonstrates how to load and validate HCL configuration files.
It uses fixed versions of the base.py and hcl_parser.py files to avoid the dataclass error.
"""

import os
import sys
import logging
from pathlib import Path
import importlib.util

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
    parser = argparse.ArgumentParser(description='UnitAPI DSL HCL Configuration Test (Simplified) - Fixed Version')
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
        # Load the fixed modules
        base_fixed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/unitapi/dsl/base_fixed.py'))
        hcl_parser_fixed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/unitapi/dsl/parsers/hcl_parser_fixed.py'))
        
        # Load the fixed base module
        base_spec = importlib.util.spec_from_file_location("unitapi.dsl.base", base_fixed_path)
        base_module = importlib.util.module_from_spec(base_spec)
        base_spec.loader.exec_module(base_module)
        
        # Replace the module in sys.modules
        sys.modules["unitapi.dsl.base"] = base_module
        
        # Load the fixed HCL parser module
        hcl_parser_spec = importlib.util.spec_from_file_location("unitapi.dsl.parsers.hcl_parser", hcl_parser_fixed_path)
        hcl_parser_module = importlib.util.module_from_spec(hcl_parser_spec)
        hcl_parser_spec.loader.exec_module(hcl_parser_module)
        
        # Replace the module in sys.modules
        sys.modules["unitapi.dsl.parsers.hcl_parser"] = hcl_parser_module
        
        # Reload the dsl module to use the fixed modules
        if "unitapi.dsl" in sys.modules:
            importlib.reload(sys.modules["unitapi.dsl"])
        
        if "unitapi.dsl.parsers" in sys.modules:
            importlib.reload(sys.modules["unitapi.dsl.parsers"])
        
        # Create a custom ConfigLoader that uses our fixed HCL parser
        class FixedConfigLoader(ConfigLoader):
            PARSERS = {
                '.yaml': 'unitapi.dsl.parsers.yaml_parser.YAMLParser',
                '.yml': 'unitapi.dsl.parsers.yaml_parser.YAMLParser',
                '.hcl': 'unitapi.dsl.parsers.hcl_parser.HCLParser',
                '.star': 'unitapi.dsl.parsers.starlark_parser.StarlarkParser',
                '.ua': 'unitapi.dsl.parsers.simple_parser.SimpleDSLParser',
            }
        
        # Load the configuration using our fixed loader
        logger.info(f"Loading configuration from {config_path}")
        config = FixedConfigLoader.load(str(config_path))
        
        # Display basic configuration info
        logger.info("Configuration loaded successfully")
        logger.info(f"Version: {config.get('version')}")
        logger.info(f"Extensions: {len(config.get('extensions', []))}")
        logger.info(f"Devices: {len(config.get('devices', []))}")
        logger.info(f"Pipelines: {len(config.get('pipelines', []))}")
        
        # Display device details
        logger.info("\nDevice Details:")
        for device in config.get('devices', []):
            logger.info(f"  - ID: {device.id}")
            logger.info(f"    Type: {device.device_type}")
            logger.info(f"    Capabilities: {', '.join(device.capabilities)}")
            if device.metadata:
                logger.info(f"    Metadata: {device.metadata}")
            logger.info("")
        
        # Convert to another format if requested
        if args.convert_to:
            converted = FixedConfigLoader.convert(config, args.convert_to)
            output_path = config_path.with_suffix(f".converted.{args.convert_to}")
            with open(output_path, 'w') as f:
                f.write(converted)
            logger.info(f"Converted configuration written to {output_path}")
            
            # Verify the converted configuration can be loaded back
            converted_config = FixedConfigLoader.load_from_string(converted, args.convert_to)
            logger.info("Converted configuration is valid")
        
        logger.info("Test completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
