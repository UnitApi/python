from typing import Dict, Any, List, Optional
from ..base import Extension, Device, Pipeline, PipelineStep, IDSLParser


class StarlarkParser(IDSLParser):
    """Starlark parser implementation for UnitAPI DSL"""

    def __init__(self):
        self.globals = {}
        self._setup_builtins()

    def _setup_builtins(self):
        """Setup built-in functions for Starlark"""

        def extension(name, version=">=1.0.0", config=None):
            """
            Define an extension

            Args:
                name: Extension name
                version: Version requirement
                config: Configuration dictionary

            Returns:
                Extension object
            """
            return Extension(
                type="extension", name=name, version=version, config=config or {}
            )

        def device(id, type="generic", capabilities=None):
            """
            Define a device

            Args:
                id: Device ID
                type: Device type
                capabilities: List of capabilities

            Returns:
                Device object
            """
            return Device(
                type="device", id=id, device_type=type, capabilities=capabilities or []
            )

        def pipeline(name, source=None, target=None, steps=None):
            """
            Define a pipeline

            Args:
                name: Pipeline name
                source: Source device ID
                target: Target device ID
                steps: List of pipeline steps

            Returns:
                Pipeline object
            """
            return Pipeline(
                type="pipeline",
                name=name,
                source=source,
                target=target,
                steps=steps or [],
            )

        def step(action, **params):
            """
            Define a pipeline step

            Args:
                action: Step action
                **params: Step parameters

            Returns:
                PipelineStep object
            """
            return PipelineStep(type="step", action=action, params=params)

        # Register built-ins
        self.globals.update(
            {
                "extension": extension,
                "device": device,
                "pipeline": pipeline,
                "step": step,
            }
        )

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse Starlark content

        Args:
            content: Starlark content as a string

        Returns:
            A dictionary containing the parsed configuration
        """
        try:
            import starlark
        except ImportError:
            raise ImportError(
                "starlark package is required for Starlark parsing. Install it with 'pip install starlark'"
            )

        # Execute Starlark code
        thread = starlark.Thread(name="unitapi_dsl_parser")
        exec_globals = self.globals.copy()

        # Add version variable
        exec_globals["VERSION"] = "1.0"

        starlark.exec_module(
            thread=thread, module_name="config", source=content, globals=exec_globals
        )

        # Extract configuration
        result = {
            "version": exec_globals.get("VERSION", "1.0"),
            "extensions": [],
            "devices": [],
            "pipelines": [],
        }

        # Process globals from executed Starlark
        for key, value in exec_globals.items():
            if key.startswith("_") or key in self.globals or key == "VERSION":
                continue

            if isinstance(value, Extension):
                result["extensions"].append(value)
            elif isinstance(value, Device):
                result["devices"].append(value)
            elif isinstance(value, Pipeline):
                result["pipelines"].append(value)

        return result

    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate Starlark configuration

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
        return True

    def to_string(self, config: Dict[str, Any]) -> str:
        """
        Convert a configuration dictionary back to Starlark string

        Args:
            config: The configuration dictionary to convert

        Returns:
            The Starlark content as a string
        """
        lines = [f'VERSION = "{config.get("version", "1.0")}"', ""]

        # Add extensions
        for i, ext in enumerate(config.get("extensions", [])):
            var_name = f"{ext.name}_ext"
            lines.append(f"{var_name} = extension(")
            lines.append(f'    name = "{ext.name}",')
            lines.append(f'    version = "{ext.version}",')

            if ext.config:
                lines.append("    config = {")
                for key, value in ext.config.items():
                    if isinstance(value, str):
                        lines.append(f'        "{key}": "{value}",')
                    else:
                        lines.append(f'        "{key}": {value},')
                lines.append("    }")

            lines.append(")")
            lines.append("")

        # Add devices
        for i, device in enumerate(config.get("devices", [])):
            var_name = f"{device.id.replace('-', '_')}"
            lines.append(f"{var_name} = device(")
            lines.append(f'    id = "{device.id}",')
            lines.append(f'    type = "{device.device_type}",')

            if device.capabilities:
                caps_str = ", ".join([f'"{cap}"' for cap in device.capabilities])
                lines.append(f"    capabilities = [{caps_str}]")

            lines.append(")")
            lines.append("")

        # Add pipelines
        for i, pipeline in enumerate(config.get("pipelines", [])):
            var_name = f"{pipeline.name.replace('-', '_')}"
            lines.append(f"{var_name} = pipeline(")
            lines.append(f'    name = "{pipeline.name}",')

            if pipeline.source:
                lines.append(f'    source = "{pipeline.source}",')

            if pipeline.target:
                lines.append(f'    target = "{pipeline.target}",')

            if pipeline.steps:
                lines.append("    steps = [")
                for step in pipeline.steps:
                    lines.append(
                        f'        step("{step.action}", '
                        + ", ".join([f"{k}={repr(v)}" for k, v in step.params.items()])
                        + "),"
                    )
                lines.append("    ]")

            lines.append(")")
            lines.append("")

        return "\n".join(lines)
