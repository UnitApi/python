import asyncio
from typing import Dict, Any, List, Optional
import logging
from ..base import Extension, Device, Pipeline, PipelineStep

logger = logging.getLogger(__name__)


class DSLExecutor:
    """Executes DSL configurations by interacting with UnitAPI"""

    def __init__(self, unitapi_instance=None):
        """
        Initialize the DSL executor

        Args:
            unitapi_instance: An instance of the UnitAPI class (optional)
        """
        self.unitapi = unitapi_instance
        self.running_pipelines = {}
        self.initialized_devices = {}
        self.loaded_extensions = {}

    def set_unitapi(self, unitapi_instance):
        """
        Set the UnitAPI instance to use

        Args:
            unitapi_instance: An instance of the UnitAPI class
        """
        self.unitapi = unitapi_instance

    async def execute_config(self, config: Dict[str, Any]):
        """
        Execute complete configuration

        Args:
            config: The parsed configuration dictionary
        """
        if self.unitapi is None:
            raise ValueError("UnitAPI instance not set. Call set_unitapi() first.")

        # Load extensions
        for ext in config.get("extensions", []):
            await self.load_extension(ext)

        # Initialize devices
        for device in config.get("devices", []):
            await self.initialize_device(device)

        # Start pipelines
        for pipeline in config.get("pipelines", []):
            await self.start_pipeline(pipeline)

    async def load_extension(self, extension: Extension):
        """
        Load and initialize extension

        Args:
            extension: Extension configuration
        """
        logger.info(f"Loading extension: {extension.name} v{extension.version}")

        if extension.name in self.loaded_extensions:
            logger.warning(f"Extension {extension.name} already loaded, skipping")
            return

        try:
            # Use UnitAPI's extension registry
            self.unitapi.registry.load_extension(
                extension.name, extension.version, extension.config or {}
            )

            self.loaded_extensions[extension.name] = extension
            logger.info(f"Extension {extension.name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load extension {extension.name}: {e}")
            raise

    async def initialize_device(self, device: Device):
        """
        Initialize device with capabilities

        Args:
            device: Device configuration
        """
        logger.info(f"Initializing device: {device.id} ({device.device_type})")

        if device.id in self.initialized_devices:
            logger.warning(f"Device {device.id} already initialized, skipping")
            return

        try:
            # Create device instance
            device_instance = self.unitapi.create_device(device.id, device.device_type)

            # Add capabilities
            for capability in device.capabilities:
                self.unitapi.add_capability(device_instance, capability)

            self.initialized_devices[device.id] = device_instance
            logger.info(f"Device {device.id} initialized successfully")

            return device_instance
        except Exception as e:
            logger.error(f"Failed to initialize device {device.id}: {e}")
            raise

    async def start_pipeline(self, pipeline: Pipeline):
        """
        Start pipeline execution

        Args:
            pipeline: Pipeline configuration
        """
        logger.info(f"Starting pipeline: {pipeline.name}")

        if pipeline.name in self.running_pipelines:
            logger.warning(f"Pipeline {pipeline.name} already running, stopping first")
            await self.stop_pipeline(pipeline.name)

        try:
            # Create pipeline instance
            pipeline_instance = self.unitapi.create_pipeline(pipeline.name)

            # Set source and target
            if pipeline.source:
                if pipeline.source not in self.initialized_devices:
                    logger.warning(
                        f"Source device {pipeline.source} not initialized, initializing now"
                    )
                    source_device = next(
                        (d for d in self.unitapi.devices if d.id == pipeline.source),
                        None,
                    )
                    if source_device:
                        await self.initialize_device(source_device)
                    else:
                        raise ValueError(f"Source device {pipeline.source} not found")

                pipeline_instance.set_source(pipeline.source)

            if pipeline.target:
                if pipeline.target not in self.initialized_devices:
                    logger.warning(
                        f"Target device {pipeline.target} not initialized, initializing now"
                    )
                    target_device = next(
                        (d for d in self.unitapi.devices if d.id == pipeline.target),
                        None,
                    )
                    if target_device:
                        await self.initialize_device(target_device)
                    else:
                        raise ValueError(f"Target device {pipeline.target} not found")

                pipeline_instance.set_target(pipeline.target)

            # Add steps
            for step in pipeline.steps:
                pipeline_instance.add_step(step.action, **step.params)

            # Start pipeline
            task = asyncio.create_task(pipeline_instance.run())
            self.running_pipelines[pipeline.name] = {
                "task": task,
                "instance": pipeline_instance,
            }

            logger.info(f"Pipeline {pipeline.name} started successfully")
            return pipeline_instance
        except Exception as e:
            logger.error(f"Failed to start pipeline {pipeline.name}: {e}")
            raise

    async def stop_pipeline(self, pipeline_name: str):
        """
        Stop running pipeline

        Args:
            pipeline_name: Name of the pipeline to stop
        """
        if pipeline_name not in self.running_pipelines:
            logger.warning(f"Pipeline {pipeline_name} not running, nothing to stop")
            return

        logger.info(f"Stopping pipeline: {pipeline_name}")

        try:
            pipeline_data = self.running_pipelines[pipeline_name]
            task = pipeline_data["task"]
            instance = pipeline_data["instance"]

            # Stop the pipeline instance
            if hasattr(instance, "stop") and callable(instance.stop):
                await instance.stop()

            # Cancel the task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            del self.running_pipelines[pipeline_name]
            logger.info(f"Pipeline {pipeline_name} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop pipeline {pipeline_name}: {e}")
            raise

    async def stop_all(self):
        """Stop all running pipelines"""
        logger.info("Stopping all pipelines")

        for pipeline_name in list(self.running_pipelines.keys()):
            await self.stop_pipeline(pipeline_name)

        logger.info("All pipelines stopped")

    async def cleanup(self):
        """Clean up resources"""
        await self.stop_all()

        # Clean up devices
        for device_id, device_instance in self.initialized_devices.items():
            if hasattr(device_instance, "cleanup") and callable(
                device_instance.cleanup
            ):
                try:
                    await device_instance.cleanup()
                    logger.info(f"Device {device_id} cleaned up")
                except Exception as e:
                    logger.error(f"Failed to clean up device {device_id}: {e}")

        self.initialized_devices = {}
        self.loaded_extensions = {}
        logger.info("Cleanup complete")
