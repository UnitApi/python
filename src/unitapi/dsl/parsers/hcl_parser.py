from typing import Dict, Any, List, Optional
from io import StringIO
from ..base import Extension, Device, Pipeline, PipelineStep, IDSLParser


class HCLParser(IDSLParser):
    """HCL parser implementation for UnitAPI DSL"""

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse HCL content

        Args:
            content: HCL content as a string

        Returns:
            A dictionary containing the parsed configuration
        """
        try:
            import hcl2
        except ImportError:
            raise ImportError(
                "python-hcl2 package is required for HCL parsing. Install it with 'pip install python-hcl2'"
            )

        # Pre-process content to handle single quotes in arrays
        # Replace single quotes with double quotes in array elements
        processed_content = self._preprocess_content(content)

        # Parse HCL using python-hcl2
        with StringIO(processed_content) as file:
            data = hcl2.load(file)

        result = {"version": "1.0", "extensions": [], "devices": [], "pipelines": []}

        # Extract version if present
        if "version" in data:
            result["version"] = data["version"]

        # Process extensions
        if "extension" in data:
            # Handle the case where extension is a list of dictionaries
            if isinstance(data["extension"], list):
                for ext_dict in data["extension"]:
                    for name, config in ext_dict.items():
                        ext = Extension(
                            type="extension",
                            name=name,
                            version=config.get("version", ">=1.0.0"),
                            config=(
                                config.get("config", [{}])[0]
                                if config.get("config")
                                else {}
                            ),
                        )
                        result["extensions"].append(ext)
            # Handle the case where extension is a dictionary
            elif isinstance(data["extension"], dict):
                for name, config in data["extension"].items():
                    ext = Extension(
                        type="extension",
                        name=name,
                        version=config.get("version", ">=1.0.0"),
                        config=config.get("config", {}),
                    )
                    result["extensions"].append(ext)

        # Process devices
        if "device" in data:
            # Handle the case where device is a list of dictionaries
            if isinstance(data["device"], list):
                for dev_dict in data["device"]:
                    for device_id, config in dev_dict.items():
                        device = Device(
                            type="device",
                            id=device_id,
                            device_type=config.get("type", "generic"),
                            capabilities=config.get("capabilities", []),
                            metadata=config.get("metadata"),
                        )
                        result["devices"].append(device)
            # Handle the case where device is a dictionary
            elif isinstance(data["device"], dict):
                for device_id, config in data["device"].items():
                    device = Device(
                        type="device",
                        id=device_id,
                        device_type=config.get("type", "generic"),
                        capabilities=config.get("capabilities", []),
                        metadata=config.get("metadata"),
                    )
                    result["devices"].append(device)

        # Process pipelines
        if "pipeline" in data:
            # Handle the case where pipeline is a list of dictionaries
            if isinstance(data["pipeline"], list):
                for pipeline_dict in data["pipeline"]:
                    for name, config in pipeline_dict.items():
                        steps = []
                        if "step" in config:
                            # Handle the case where step is a list of dictionaries
                            if isinstance(config["step"], list):
                                for step_dict in config["step"]:
                                    for step_name, step_config in step_dict.items():
                                        step = PipelineStep(
                                            type="step",
                                            action=step_name,
                                            params=step_config,
                                        )
                                        steps.append(step)
                            # Handle the case where step is a dictionary
                            elif isinstance(config["step"], dict):
                                for step_name, step_config in config["step"].items():
                                    step = PipelineStep(
                                        type="step",
                                        action=step_name,
                                        params=step_config,
                                    )
                                    steps.append(step)

                        pipeline = Pipeline(
                            type="pipeline",
                            name=name,
                            source=config.get("source"),
                            target=config.get("target"),
                            steps=steps,
                        )
                        result["pipelines"].append(pipeline)
            # Handle the case where pipeline is a dictionary
            elif isinstance(data["pipeline"], dict):
                for name, config in data["pipeline"].items():
                    steps = []
                    if "step" in config:
                        # Handle the case where step is a list of dictionaries
                        if isinstance(config["step"], list):
                            for step_dict in config["step"]:
                                for step_name, step_config in step_dict.items():
                                    step = PipelineStep(
                                        type="step",
                                        action=step_name,
                                        params=step_config,
                                    )
                                    steps.append(step)
                        # Handle the case where step is a dictionary
                        elif isinstance(config["step"], dict):
                            for step_name, step_config in config["step"].items():
                                step = PipelineStep(
                                    type="step", action=step_name, params=step_config
                                )
                                steps.append(step)

                    pipeline = Pipeline(
                        type="pipeline",
                        name=name,
                        source=config.get("source"),
                        target=config.get("target"),
                        steps=steps,
                    )
                    result["pipelines"].append(pipeline)

        return result

    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess HCL content to handle single quotes in arrays

        Args:
            content: The original HCL content

        Returns:
            Processed HCL content with single quotes replaced with double quotes in arrays
        """
        import re

        # Find array patterns with single quotes and replace them with double quotes
        # This regex looks for array patterns like colors = ['red', 'green', 'blue']
        array_pattern = r"(\w+\s*=\s*\[)(.*?)(\])"

        def replace_single_quotes_in_array(match):
            prefix = match.group(1)  # The part before the array content
            array_content = match.group(2)  # The array content
            suffix = match.group(3)  # The closing bracket

            # Replace single quotes with double quotes in the array content
            # This handles both 'string' and "string" formats
            processed_content = re.sub(r"'([^']*)'", r'"\1"', array_content)

            return prefix + processed_content + suffix

        # Apply the replacement
        processed_content = re.sub(
            array_pattern, replace_single_quotes_in_array, content, flags=re.DOTALL
        )

        return processed_content

    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate HCL configuration

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
        Convert a configuration dictionary back to HCL string

        Args:
            config: The configuration dictionary to convert

        Returns:
            The HCL content as a string
        """
        lines = [f'version = "{config.get("version", "1.0")}"', ""]

        # Add extensions
        for ext in config.get("extensions", []):
            lines.append(f'extension "{ext.name}" {{')
            lines.append(f'  version = "{ext.version}"')

            if ext.config:
                lines.append("  config {")
                for key, value in ext.config.items():
                    if isinstance(value, str):
                        lines.append(f'    {key} = "{value}"')
                    elif isinstance(value, bool):
                        # Convert Python's True/False to lowercase true/false for HCL
                        lines.append(f"    {key} = {str(value).lower()}")
                    else:
                        lines.append(f"    {key} = {value}")
                lines.append("  }")

            lines.append("}")
            lines.append("")

        # Add devices
        for device in config.get("devices", []):
            lines.append(f'device "{device.id}" {{')
            lines.append(f'  type = "{device.device_type}"')

            if device.capabilities:
                capabilities_str = ", ".join(
                    [f'"{cap}"' for cap in device.capabilities]
                )
                lines.append(f"  capabilities = [{capabilities_str}]")

            if device.metadata:
                lines.append("  metadata = {")
                for key, value in device.metadata.items():
                    if isinstance(value, str):
                        lines.append(f'    {key} = "{value}"')
                    elif isinstance(value, bool):
                        # Convert Python's True/False to lowercase true/false for HCL
                        lines.append(f"    {key} = {str(value).lower()}")
                    else:
                        lines.append(f"    {key} = {value}")
                lines.append("  }")

            lines.append("}")
            lines.append("")

        # Add pipelines
        for pipeline in config.get("pipelines", []):
            lines.append(f'pipeline "{pipeline.name}" {{')

            if pipeline.source:
                lines.append(f'  source = "{pipeline.source}"')

            if pipeline.target:
                lines.append(f'  target = "{pipeline.target}"')

            for step in pipeline.steps:
                lines.append(f'  step "{step.action}" {{')

                for key, value in step.params.items():
                    if isinstance(value, str):
                        lines.append(f'    {key} = "{value}"')
                    elif isinstance(value, list):
                        values = []
                        for v in value:
                            if isinstance(v, str):
                                # Ensure strings are properly quoted with double quotes
                                values.append(f'"{v}"')
                            elif isinstance(v, bool):
                                # Convert Python's True/False to lowercase true/false for HCL
                                values.append(str(v).lower())
                            else:
                                values.append(str(v))
                        values_str = ", ".join(values)
                        lines.append(f"    {key} = [{values_str}]")
                    elif isinstance(value, bool):
                        # Convert Python's True/False to lowercase true/false for HCL
                        lines.append(f"    {key} = {str(value).lower()}")
                    else:
                        lines.append(f"    {key} = {value}")

                lines.append("  }")

            lines.append("}")
            lines.append("")

        return "\n".join(lines)
