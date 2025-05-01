import os
import importlib
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Universal configuration loader supporting multiple formats"""

    # Mapping of file extensions to parser classes
    PARSERS = {
        ".yaml": "unitapi.dsl.parsers.yaml_parser.YAMLParser",
        ".yml": "unitapi.dsl.parsers.yaml_parser.YAMLParser",
        ".hcl": "unitapi.dsl.parsers.hcl_parser.HCLParser",
        ".star": "unitapi.dsl.parsers.starlark_parser.StarlarkParser",
        ".ua": "unitapi.dsl.parsers.simple_parser.SimpleDSLParser",
    }

    @classmethod
    def load(cls, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from file

        Args:
            file_path: Path to the configuration file

        Returns:
            A dictionary containing the parsed configuration

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported or the configuration is invalid
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix not in cls.PARSERS:
            raise ValueError(f"Unsupported configuration format: {suffix}")

        # Dynamic import of parser
        parser_path = cls.PARSERS[suffix]
        module_name, class_name = parser_path.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
            parser_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import parser {parser_path}: {e}")

        # Parse configuration
        parser = parser_class()

        with open(file_path, "r") as f:
            content = f.read()

        try:
            config = parser.parse(content)
        except Exception as e:
            raise ValueError(f"Failed to parse configuration: {e}")

        # Validate configuration
        if not parser.validate(config):
            raise ValueError("Invalid configuration")

        return config

    @classmethod
    def load_from_string(cls, content: str, format: str) -> Dict[str, Any]:
        """
        Load configuration from string with specified format

        Args:
            content: The configuration content as a string
            format: The format of the configuration (yaml, hcl, star, ua)

        Returns:
            A dictionary containing the parsed configuration

        Raises:
            ValueError: If the format is not supported or the configuration is invalid
        """
        format = format.lower()
        format_map = {
            "yaml": ".yaml",
            "yml": ".yml",
            "hcl": ".hcl",
            "star": ".star",
            "starlark": ".star",
            "ua": ".ua",
            "simple": ".ua",
        }

        if format not in format_map:
            raise ValueError(f"Unsupported configuration format: {format}")

        suffix = format_map[format]

        # Dynamic import of parser
        parser_path = cls.PARSERS[suffix]
        module_name, class_name = parser_path.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
            parser_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import parser {parser_path}: {e}")

        # Parse configuration
        parser = parser_class()

        try:
            config = parser.parse(content)
        except Exception as e:
            raise ValueError(f"Failed to parse configuration: {e}")

        # Validate configuration
        if not parser.validate(config):
            raise ValueError("Invalid configuration")

        return config

    @classmethod
    def convert(cls, config: Dict[str, Any], target_format: str) -> str:
        """
        Convert configuration to a different format

        Args:
            config: The configuration dictionary
            target_format: The target format (yaml, hcl, star, ua)

        Returns:
            The configuration as a string in the target format

        Raises:
            ValueError: If the target format is not supported
        """
        target_format = target_format.lower()
        format_map = {
            "yaml": ".yaml",
            "yml": ".yml",
            "hcl": ".hcl",
            "star": ".star",
            "starlark": ".star",
            "ua": ".ua",
            "simple": ".ua",
        }

        if target_format not in format_map:
            raise ValueError(f"Unsupported target format: {target_format}")

        suffix = format_map[target_format]

        # Dynamic import of parser
        parser_path = cls.PARSERS[suffix]
        module_name, class_name = parser_path.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
            parser_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to import parser {parser_path}: {e}")

        # Convert configuration
        parser = parser_class()

        try:
            return parser.to_string(config)
        except Exception as e:
            raise ValueError(f"Failed to convert configuration: {e}")

    @classmethod
    def convert_file(
        cls, source_file: str, target_format: str, output_file: Optional[str] = None
    ) -> str:
        """
        Convert configuration file to a different format

        Args:
            source_file: Path to the source configuration file
            target_format: The target format (yaml, hcl, star, ua)
            output_file: Path to the output file (optional)

        Returns:
            The configuration as a string in the target format

        Raises:
            FileNotFoundError: If the source file doesn't exist
            ValueError: If the source format or target format is not supported
        """
        # Load source configuration
        config = cls.load(source_file)

        # Convert to target format
        result = cls.convert(config, target_format)

        # Write to output file if specified
        if output_file:
            with open(output_file, "w") as f:
                f.write(result)

        return result
