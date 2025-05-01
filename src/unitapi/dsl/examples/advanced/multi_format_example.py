"""
Advanced example showing how to use multiple DSL formats together
"""

import asyncio
import os
import logging
from pathlib import Path

from unitapi import UnitAPI
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.runtime.executor import DSLExecutor
from unitapi.dsl.runtime.context import DSLContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main function"""
    # Create a UnitAPI instance
    unitapi = UnitAPI()

    # Create a DSL executor
    executor = DSLExecutor(unitapi)

    # Create a DSL context
    context = DSLContext()

    # Load base configuration from YAML
    base_config_path = Path(__file__).parent / "base_config.yaml"
    logger.info(f"Loading base configuration from {base_config_path}")
    base_config = ConfigLoader.load(str(base_config_path))

    # Load device-specific configuration from HCL
    devices_config_path = Path(__file__).parent / "devices.hcl"
    logger.info(f"Loading device configuration from {devices_config_path}")
    device_config = ConfigLoader.load(str(devices_config_path))

    # Merge configurations
    logger.info("Merging configurations")
    base_config["devices"].extend(device_config["devices"])

    # Load dynamic pipeline configuration from Starlark
    pipelines_config_path = Path(__file__).parent / "pipelines.star"
    logger.info(f"Loading pipeline configuration from {pipelines_config_path}")
    pipeline_config = ConfigLoader.load(str(pipelines_config_path))

    # Replace pipelines with dynamically generated ones
    base_config["pipelines"] = pipeline_config["pipelines"]

    # Execute combined configuration
    logger.info("Executing combined configuration")
    await executor.execute_config(base_config)

    # Register event handlers
    logger.info("Registering event handlers")
    context.register_event_handler("state_changed:temperature", temperature_handler)

    # Keep running until interrupted
    try:
        logger.info("Running... Press Ctrl+C to stop")
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


async def temperature_handler(event_name, event_data):
    """Handle temperature state changes"""
    logger.info(f"Temperature changed: {event_data}")

    # Example of taking action based on temperature
    if event_data["new_value"] > 80:
        logger.warning(f"Temperature too high: {event_data['new_value']}")
        # Take action, e.g., send alert


if __name__ == "__main__":
    asyncio.run(main())
