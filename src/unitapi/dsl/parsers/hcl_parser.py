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
            raise ImportError("python-hcl2 package is required for HCL parsing. Install it with 'pip install python-hcl2'")
        
        # Parse HCL using python-hcl2
        with StringIO(content) as file:
            data = hcl2.load(file)
        
        result = {
            "version": "1.0",
            "extensions": [],
            "devices": [],
            "pipelines": []
        }
        
        # Extract version if present
        if 'version' in data:
            result["version"] = data['version']
        
        # Process extensions
        if 'extension' in data:
            for name, config in data['extension'].items():
                ext = Extension(
                    type="extension",
                    name=name,
                    version=config.get('version', '>=1.0.0'),
                    config=config.get('config', {})
                )
                result["extensions"].append(ext)
        
        # Process devices
        if 'device' in data:
            for device_id, config in data['device'].items():
                device = Device(
                    type="device",
                    id=device_id,
                    device_type=config.get('type', 'generic'),
                    capabilities=config.get('capabilities', [])
                )
                result["devices"].append(device)
        
        # Process pipelines
        if 'pipeline' in data:
            for name, config in data['pipeline'].items():
                steps = []
                if 'step' in config:
                    for step_name, step_config in config['step'].items():
                        step = PipelineStep(
                            type="step",
                            action=step_name,
                            params=step_config
                        )
                        steps.append(step)
                
                pipeline = Pipeline(
                    type="pipeline",
                    name=name,
                    source=config.get('source'),
                    target=config.get('target'),
                    steps=steps
                )
                result["pipelines"].append(pipeline)
        
        return result
    
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
                lines.append('  config {')
                for key, value in ext.config.items():
                    if isinstance(value, str):
                        lines.append(f'    {key} = "{value}"')
                    else:
                        lines.append(f'    {key} = {value}')
                lines.append('  }')
            
            lines.append('}')
            lines.append('')
        
        # Add devices
        for device in config.get("devices", []):
            lines.append(f'device "{device.id}" {{')
            lines.append(f'  type = "{device.device_type}"')
            
            if device.capabilities:
                capabilities_str = ', '.join([f'"{cap}"' for cap in device.capabilities])
                lines.append(f'  capabilities = [{capabilities_str}]')
            
            lines.append('}')
            lines.append('')
        
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
                        values_str = ', '.join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                        lines.append(f'    {key} = [{values_str}]')
                    else:
                        lines.append(f'    {key} = {value}')
                
                lines.append('  }')
            
            lines.append('}')
            lines.append('')
        
        return '\n'.join(lines)
