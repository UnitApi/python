import re
from typing import Dict, Any, List, Optional
from ..base import Extension, Device, Pipeline, PipelineStep, IDSLParser

class SimpleDSLParser(IDSLParser):
    """Simple shell-like DSL parser for UnitAPI"""
    
    def __init__(self):
        self.result = {
            "version": "1.0",
            "extensions": [],
            "devices": [],
            "pipelines": []
        }
        self.current_pipeline = None
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse simple DSL content
        
        Args:
            content: Simple DSL content as a string
            
        Returns:
            A dictionary containing the parsed configuration
        """
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            self._parse_line(line)
        
        return self.result
    
    def _parse_line(self, line: str):
        """Parse a single line of DSL"""
        # Version definition
        if line.startswith('version'):
            match = re.match(r'version\s+"([^"]+)"', line)
            if match:
                self.result["version"] = match.group(1)
        
        # Load extension
        elif line.startswith('load'):
            self._parse_load(line)
        
        # Device definition
        elif line.startswith('device'):
            self._parse_device(line)
        
        # Pipeline definition
        elif line.startswith('pipeline'):
            self._parse_pipeline(line)
        
        # Pipeline steps
        elif self.current_pipeline and ':' not in line and line != 'end':
            self._parse_pipeline_step(line)
        
        # End of pipeline
        elif line == 'end':
            self.current_pipeline = None
    
    def _parse_load(self, line: str):
        """Parse load extension command"""
        match = re.match(r'load\s+(\w+)(?:\s+version="([^"]+)")?(?:\s+config=(.+))?', line)
        if match:
            name = match.group(1)
            version = match.group(2) or ">=1.0.0"
            config = {}
            
            # Parse config if present
            if match.group(3):
                config_str = match.group(3)
                if config_str.startswith('{') and config_str.endswith('}'):
                    # Parse JSON-like config
                    config_str = config_str[1:-1]  # Remove braces
                    for item in config_str.split(','):
                        if ':' in item:
                            key, value = item.split(':', 1)
                            key = key.strip().strip('"\'')
                            value = value.strip().strip('"\'')
                            config[key] = value
            
            extension = Extension(
                type="extension",
                name=name,
                version=version,
                config=config
            )
            self.result["extensions"].append(extension)
    
    def _parse_device(self, line: str):
        """Parse device definition"""
        match = re.match(r'device\s+(\w+(?:-\w+)*)\s+type=(\w+)(?:\s+with\s+(.+))?', line)
        if match:
            device_id = match.group(1)
            device_type = match.group(2)
            capabilities = []
            if match.group(3):
                capabilities = [cap.strip() for cap in match.group(3).split(',')]
            
            device = Device(
                type="device",
                id=device_id,
                device_type=device_type,
                capabilities=capabilities
            )
            self.result["devices"].append(device)
    
    def _parse_pipeline(self, line: str):
        """Parse pipeline definition"""
        # Pipeline with source and target
        match = re.match(r'pipeline\s+(\w+(?:-\w+)*)(?:\s+from\s+(\w+(?:-\w+)*)(?:\s+to\s+(\w+(?:-\w+)*))?)?:', line)
        if match:
            name = match.group(1)
            source = match.group(2)
            target = match.group(3)
            
            self.current_pipeline = Pipeline(
                type="pipeline",
                name=name,
                source=source,
                target=target,
                steps=[]
            )
            self.result["pipelines"].append(self.current_pipeline)
    
    def _parse_pipeline_step(self, line: str):
        """Parse pipeline step"""
        if not self.current_pipeline:
            return
        
        # Parse step with parameters
        parts = line.split()
        if not parts:
            return
        
        action = parts[0]
        params = {}
        
        # Parse parameters
        i = 1
        while i < len(parts):
            if '=' in parts[i]:
                key, value = parts[i].split('=', 1)
                
                # Handle quoted values
                if value.startswith('"') and value.endswith('"'):
                    params[key] = value[1:-1]
                # Handle list values
                elif value.startswith('[') and value.endswith(']'):
                    value_list = value[1:-1].split(',')
                    params[key] = [v.strip().strip('"\'') for v in value_list]
                # Handle numeric values
                elif value.isdigit():
                    params[key] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    params[key] = float(value)
                else:
                    params[key] = value
            else:
                # Handle positional parameters
                if action == 'filter' and i == 1:
                    # Special case for filter keys
                    params['keys'] = parts[i].split(',')
                elif action == 'capture' and i == 1:
                    # Special case for capture device
                    params['device'] = parts[i]
            
            i += 1
        
        step = PipelineStep(
            type="step",
            action=action,
            params=params
        )
        self.current_pipeline.steps.append(step)
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate simple DSL configuration
        
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
        Convert a configuration dictionary back to simple DSL string
        
        Args:
            config: The configuration dictionary to convert
            
        Returns:
            The simple DSL content as a string
        """
        lines = [f'version "{config.get("version", "1.0")}"', ""]
        
        # Add extensions
        if config.get("extensions"):
            lines.append("# Load extensions")
            for ext in config.get("extensions", []):
                line = f'load {ext.name} version="{ext.version}"'
                
                if ext.config:
                    config_parts = []
                    for key, value in ext.config.items():
                        if isinstance(value, str):
                            config_parts.append(f'{key}:"{value}"')
                        else:
                            config_parts.append(f'{key}:{value}')
                    
                    line += f' config={{{",".join(config_parts)}}}'
                
                lines.append(line)
            lines.append("")
        
        # Add devices
        if config.get("devices"):
            lines.append("# Define devices")
            for device in config.get("devices", []):
                line = f'device {device.id} type={device.device_type}'
                
                if device.capabilities:
                    line += f' with {",".join(device.capabilities)}'
                
                lines.append(line)
            lines.append("")
        
        # Add pipelines
        if config.get("pipelines"):
            lines.append("# Define pipelines")
            for pipeline in config.get("pipelines", []):
                line = f'pipeline {pipeline.name}'
                
                if pipeline.source:
                    line += f' from {pipeline.source}'
                    
                    if pipeline.target:
                        line += f' to {pipeline.target}'
                
                line += ':'
                lines.append(line)
                
                # Add steps
                for step in pipeline.steps:
                    step_line = f'  {step.action}'
                    
                    # Special handling for common parameters
                    if 'device' in step.params and step.action == 'capture':
                        step_line += f' {step.params["device"]}'
                    elif 'keys' in step.params and step.action == 'filter':
                        step_line += f' {",".join(step.params["keys"])}'
                    else:
                        # Add all parameters
                        for key, value in step.params.items():
                            if isinstance(value, list):
                                step_line += f' {key}=[{",".join(str(v) for v in value)}]'
                            elif isinstance(value, str) and ' ' in value:
                                step_line += f' {key}="{value}"'
                            else:
                                step_line += f' {key}={value}'
                    
                    lines.append(step_line)
                
                lines.append('end')
                lines.append('')
        
        return '\n'.join(lines)
