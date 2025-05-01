import yaml
from typing import Dict, Any, List, Optional, Union
from io import StringIO
from ..base import DSLElement, Extension, Device, Pipeline, PipelineStep, IDSLParser


class UnitAPIYAMLLoader(yaml.SafeLoader):
    """Custom YAML loader for UnitAPI DSL with custom tags"""

    pass


def extension_constructor(loader: UnitAPIYAMLLoader, node: yaml.Node) -> Extension:
    """Constructor for !extension tag"""
    if isinstance(node, yaml.ScalarNode):
        # Simple form: !extension keyboard
        name = loader.construct_scalar(node)
        return Extension(type="extension", name=name, version="latest")
    else:
        # Full form with attributes
        data = loader.construct_mapping(node)
        name = data.pop("name", "unknown")
        version = data.pop("version", "latest")
        config = data.pop("config", {})
        return Extension(type="extension", name=name, version=version, config=config)


def device_constructor(loader: UnitAPIYAMLLoader, node: yaml.Node) -> Device:
    """Constructor for !device tag"""
    data = loader.construct_mapping(node)
    device_id = data.pop("id", "unknown")
    device_type = data.pop("device_type", "generic")
    capabilities = data.pop("capabilities", [])
    return Device(
        type="device", id=device_id, device_type=device_type, capabilities=capabilities
    )


def pipeline_constructor(loader: UnitAPIYAMLLoader, node: yaml.Node) -> Pipeline:
    """Constructor for !pipeline tag"""
    data = loader.construct_mapping(node)
    name = data.pop("name", "unknown")
    source = data.pop("source", None)
    target = data.pop("target", None)

    # Convert steps to PipelineStep objects
    steps = []
    if "steps" in data:
        for step_data in data.pop("steps", []):
            action = step_data.pop("action", "unknown")
            params = step_data.pop("params", {})
            steps.append(PipelineStep(type="step", action=action, params=params))

    return Pipeline(
        type="pipeline", name=name, source=source, target=target, steps=steps
    )


# Register constructors
UnitAPIYAMLLoader.add_constructor("!extension", extension_constructor)
UnitAPIYAMLLoader.add_constructor("!device", device_constructor)
UnitAPIYAMLLoader.add_constructor("!pipeline", pipeline_constructor)


# Custom YAML representers for DSL classes
def extension_representer(dumper, data):
    """Representer for Extension objects"""
    return dumper.represent_mapping(
        "!extension",
        {"name": data.name, "version": data.version, "config": data.config},
    )


def device_representer(dumper, data):
    """Representer for Device objects"""
    return dumper.represent_mapping(
        "!device",
        {
            "id": data.id,
            "device_type": data.device_type,
            "capabilities": data.capabilities,
        },
    )


def pipeline_step_representer(dumper, data):
    """Representer for PipelineStep objects"""
    return dumper.represent_mapping(
        "!step", {"action": data.action, "params": data.params}
    )


def pipeline_representer(dumper, data):
    """Representer for Pipeline objects"""
    mapping = {"name": data.name, "steps": data.steps}
    if data.source:
        mapping["source"] = data.source
    if data.target:
        mapping["target"] = data.target
    return dumper.represent_mapping("!pipeline", mapping)


# Register representers
yaml.add_representer(Extension, extension_representer)
yaml.add_representer(Device, device_representer)
yaml.add_representer(PipelineStep, pipeline_step_representer)
yaml.add_representer(Pipeline, pipeline_representer)


class YAMLParser(IDSLParser):
    """YAML parser implementation with custom tags for UnitAPI DSL"""

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML content with custom tags

        Args:
            content: YAML content as a string

        Returns:
            A dictionary containing the parsed configuration
        """
        # Load YAML with custom loader
        data = yaml.load(content, Loader=UnitAPIYAMLLoader)

        if not isinstance(data, dict):
            raise ValueError("Invalid YAML: root element must be a mapping")

        # Convert to standardized format
        result = {
            "version": data.get("version", "1.0"),
            "extensions": [],
            "devices": [],
            "pipelines": [],
        }

        # Process elements
        for key, value in data.items():
            if key == "extensions" and isinstance(value, list):
                for item in value:
                    if isinstance(item, Extension):
                        result["extensions"].append(item)
            elif key == "devices" and isinstance(value, list):
                for item in value:
                    if isinstance(item, Device):
                        result["devices"].append(item)
            elif key == "pipelines" and isinstance(value, list):
                for item in value:
                    if isinstance(item, Pipeline):
                        result["pipelines"].append(item)

        return result

    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate YAML configuration

        Args:
            config: The parsed configuration dictionary

        Returns:
            True if the configuration is valid, False otherwise
        """
        # Basic validation
        if not isinstance(config, dict):
            return False

        if "version" not in config:
            return False

        # More detailed validation could be added here
        # For now, we'll just check the basic structure
        return True

    def to_string(self, config: Dict[str, Any]) -> str:
        """
        Convert a configuration dictionary back to YAML string

        Args:
            config: The configuration dictionary to convert

        Returns:
            The YAML content as a string
        """
        # Create a new dictionary for the output that doesn't use custom tags
        output = {"version": config.get("version", "1.0")}

        # Convert extensions to dictionaries
        if config.get("extensions"):
            extensions = []
            for ext in config["extensions"]:
                ext_dict = {
                    "name": ext.name,
                    "version": ext.version,
                    "config": ext.config,
                }
                extensions.append(ext_dict)
            output["extensions"] = extensions

        # Convert devices to dictionaries
        if config.get("devices"):
            devices = []
            for device in config["devices"]:
                device_dict = {
                    "id": device.id,
                    "device_type": device.device_type,
                    "capabilities": device.capabilities,
                }
                devices.append(device_dict)
            output["devices"] = devices

        # Convert pipelines to dictionaries
        if config.get("pipelines"):
            pipelines = []
            for pipeline in config["pipelines"]:
                steps = []
                for step in pipeline.steps:
                    step_dict = {"action": step.action, "params": step.params}
                    steps.append(step_dict)

                pipeline_dict = {"name": pipeline.name, "steps": steps}

                if pipeline.source:
                    pipeline_dict["source"] = pipeline.source
                if pipeline.target:
                    pipeline_dict["target"] = pipeline.target

                pipelines.append(pipeline_dict)
            output["pipelines"] = pipelines

        # Convert to YAML
        return yaml.dump(output, default_flow_style=False)
