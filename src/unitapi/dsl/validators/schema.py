import re
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator


class ExtensionSchema(BaseModel):
    """Schema for extension configuration"""

    name: str
    version: str = ">=1.0.0"
    config: Dict[str, Any] = Field(default_factory=dict)

    @validator("name")
    def validate_name(cls, v):
        """Validate extension name format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Extension name must contain only letters, numbers, underscores, and hyphens"
            )
        return v

    @validator("version")
    def validate_version(cls, v):
        """Validate version format"""
        if not re.match(r"^(>=?|<=?|==?|~=)?\d+(\.\d+)*$", v):
            raise ValueError("Invalid version format")
        return v


class DeviceSchema(BaseModel):
    """Schema for device configuration"""

    id: str
    device_type: str
    capabilities: List[str] = Field(default_factory=list)

    @validator("id")
    def validate_id(cls, v):
        """Validate device ID format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Device ID must contain only letters, numbers, underscores, and hyphens"
            )
        return v

    @validator("device_type")
    def validate_device_type(cls, v):
        """Validate device type"""
        valid_types = [
            "computer",
            "raspberry_pi",
            "arduino",
            "esp32",
            "esp8266",
            "jetson",
            "smartphone",
            "tablet",
            "camera",
            "microphone",
            "speaker",
            "display",
            "keyboard",
            "mouse",
            "gamepad",
            "touchscreen",
            "gpio",
            "sensor",
            "actuator",
            "robot",
            "custom",
            "virtual_microphone",
            "raspberry_pi_microphone",
            "raspberry_pi_camera",
            "virtual_camera",
            "virtual_speaker",
            "raspberry_pi_speaker",
            "raspberry_pi_gpio",
            # Additional device types found in examples
            "mobile_touchscreen",
            "arduino_gpio",
            "esp32_gpio",
            "test_type",
            "gaming_keyboard",
            "gaming_mouse",
        ]

        # Check if the device type is in the valid list or starts with a valid prefix
        valid_prefixes = ["custom_", "virtual_", "raspberry_pi_", "arduino_", "esp32_"]

        if v in valid_types:
            return v

        for prefix in valid_prefixes:
            if v.startswith(prefix):
                return v

        raise ValueError(
            f"Invalid device type. Must be one of {valid_types} or start with one of {valid_prefixes}"
        )
        return v


class PipelineStepSchema(BaseModel):
    """Schema for pipeline step"""

    action: str
    params: Dict[str, Any] = Field(default_factory=dict)

    @validator("action")
    def validate_action(cls, v):
        """Validate step action"""
        valid_actions = [
            "capture",
            "filter",
            "transform",
            "forward",
            "publish",
            "subscribe",
            "read",
            "write",
            "detect",
            "recognize",
            "analyze",
            "process",
            "on",
            "trigger",
            "alert",
            "log",
            "custom",
            "record",
            "listen",
            "recognize",
            "process_command",
            "respond",
            "visualize",
            "display",
            "save",
            # Additional actions found in examples
            "configure",
            "set_state",
            "pwm_control",
            "on_change",
            "set_remote",
            "monitor",
            "automation",
            "map",
            "execute",
            "capture_image",
            "record_video",
            "test_step",
        ]

        if v in valid_actions or v.startswith("custom_"):
            return v

        raise ValueError(
            f"Invalid action. Must be one of {valid_actions} or start with 'custom_'"
        )
        return v


class PipelineSchema(BaseModel):
    """Schema for pipeline configuration"""

    name: str
    source: Optional[str] = None
    target: Optional[str] = None
    steps: List[PipelineStepSchema] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, v):
        """Validate pipeline name format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Pipeline name must contain only letters, numbers, underscores, and hyphens"
            )
        return v


class ConfigSchema(BaseModel):
    """Main configuration schema"""

    version: str = "1.0"
    extensions: List[ExtensionSchema] = Field(default_factory=list)
    devices: List[DeviceSchema] = Field(default_factory=list)
    pipelines: List[PipelineSchema] = Field(default_factory=list)

    @validator("version")
    def validate_version(cls, v):
        """Validate config version"""
        if v not in ["1.0", "1.1", "2.0"]:
            raise ValueError(f"Unsupported config version: {v}")
        return v

    @validator("devices")
    def validate_unique_device_ids(cls, v):
        """Validate that device IDs are unique"""
        ids = [device.id for device in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Device IDs must be unique")
        return v

    @validator("pipelines")
    def validate_unique_pipeline_names(cls, v):
        """Validate that pipeline names are unique"""
        names = [pipeline.name for pipeline in v]
        if len(names) != len(set(names)):
            raise ValueError("Pipeline names must be unique")
        return v

    @validator("pipelines")
    def validate_pipeline_references(cls, v, values):
        """Validate that pipeline source and target references exist"""
        if "devices" not in values:
            return v

        device_ids = [device.id for device in values["devices"]]

        for pipeline in v:
            if pipeline.source and pipeline.source not in device_ids:
                raise ValueError(
                    f"Pipeline '{pipeline.name}' references non-existent source device '{pipeline.source}'"
                )

            if pipeline.target and pipeline.target not in device_ids:
                raise ValueError(
                    f"Pipeline '{pipeline.name}' references non-existent target device '{pipeline.target}'"
                )

        return v


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration against schema

    Args:
        config: The configuration dictionary to validate

    Returns:
        True if the configuration is valid, False otherwise
    """
    try:
        # Convert dataclass objects to dictionaries if needed
        processed_config = {
            "version": config.get("version", "1.0"),
            "extensions": [],
            "devices": [],
            "pipelines": [],
        }

        for ext in config.get("extensions", []):
            if hasattr(ext, "__dict__"):
                # Convert dataclass to dict
                ext_dict = {
                    "name": ext.name,
                    "version": ext.version,
                    "config": ext.config,
                }
                processed_config["extensions"].append(ext_dict)
            else:
                processed_config["extensions"].append(ext)

        for device in config.get("devices", []):
            if hasattr(device, "__dict__"):
                # Convert dataclass to dict
                device_dict = {
                    "id": device.id,
                    "device_type": device.device_type,
                    "capabilities": device.capabilities,
                }
                processed_config["devices"].append(device_dict)
            else:
                processed_config["devices"].append(device)

        for pipeline in config.get("pipelines", []):
            if hasattr(pipeline, "__dict__"):
                # Convert dataclass to dict
                pipeline_dict = {
                    "name": pipeline.name,
                    "source": pipeline.source,
                    "target": pipeline.target,
                    "steps": [],
                }

                for step in pipeline.steps:
                    if hasattr(step, "__dict__"):
                        step_dict = {"action": step.action, "params": step.params}
                        pipeline_dict["steps"].append(step_dict)
                    else:
                        pipeline_dict["steps"].append(step)

                processed_config["pipelines"].append(pipeline_dict)
            else:
                processed_config["pipelines"].append(pipeline)

        # Validate against schema
        ConfigSchema(**processed_config)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


def validate_config_with_details(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate configuration against schema and return error details

    Args:
        config: The configuration dictionary to validate

    Returns:
        A tuple of (is_valid, error_message)
    """
    try:
        # Same processing as validate_config
        processed_config = {
            "version": config.get("version", "1.0"),
            "extensions": [],
            "devices": [],
            "pipelines": [],
        }

        for ext in config.get("extensions", []):
            if hasattr(ext, "__dict__"):
                ext_dict = {
                    "name": ext.name,
                    "version": ext.version,
                    "config": ext.config,
                }
                processed_config["extensions"].append(ext_dict)
            else:
                processed_config["extensions"].append(ext)

        for device in config.get("devices", []):
            if hasattr(device, "__dict__"):
                device_dict = {
                    "id": device.id,
                    "device_type": device.device_type,
                    "capabilities": device.capabilities,
                }
                processed_config["devices"].append(device_dict)
            else:
                processed_config["devices"].append(device)

        for pipeline in config.get("pipelines", []):
            if hasattr(pipeline, "__dict__"):
                pipeline_dict = {
                    "name": pipeline.name,
                    "source": pipeline.source,
                    "target": pipeline.target,
                    "steps": [],
                }

                for step in pipeline.steps:
                    if hasattr(step, "__dict__"):
                        step_dict = {"action": step.action, "params": step.params}
                        pipeline_dict["steps"].append(step_dict)
                    else:
                        pipeline_dict["steps"].append(step)

                processed_config["pipelines"].append(pipeline_dict)
            else:
                processed_config["pipelines"].append(pipeline)

        # Validate against schema
        ConfigSchema(**processed_config)
        return True, None
    except Exception as e:
        return False, str(e)
