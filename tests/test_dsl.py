import pytest
import os
from pathlib import Path
import tempfile
import yaml

from unitapi.config.loader import ConfigLoader
from unitapi.dsl.parsers.yaml_parser import YAMLParser
from unitapi.dsl.parsers.hcl_parser import HCLParser
from unitapi.dsl.parsers.starlark_parser import StarlarkParser
from unitapi.dsl.parsers.simple_parser import SimpleDSLParser
from unitapi.dsl.validators.schema import validate_config, validate_config_with_details
from unitapi.dsl.base import Extension, Device, Pipeline, PipelineStep


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "version": "1.0",
        "extensions": [
            Extension(
                type="extension",
                name="keyboard",
                version=">=1.0.0",
                config={"layout": "us"},
            )
        ],
        "devices": [
            Device(
                type="device",
                id="pc-main",
                device_type="computer",
                capabilities=["keyboard", "mouse"],
            )
        ],
        "pipelines": [
            Pipeline(
                type="pipeline",
                name="test-pipeline",
                source="pc-main",
                steps=[
                    PipelineStep(
                        type="step", action="capture", params={"device": "keyboard"}
                    )
                ],
            )
        ],
    }


@pytest.fixture
def yaml_content():
    """Sample YAML content for testing"""
    return """
version: "1.0"

extensions:
  - !extension
    name: keyboard
    version: ">=1.0.0"
    config:
      layout: "us"

devices:
  - !device
    id: "pc-main"
    device_type: "computer"
    capabilities: ["keyboard", "mouse"]

pipelines:
  - !pipeline
    name: "test-pipeline"
    source: "pc-main"
    steps:
      - action: "capture"
        params:
          device: "keyboard"
"""


@pytest.fixture
def hcl_content():
    """Sample HCL content for testing"""
    return """
version = "1.0"

extension "keyboard" {
  version = ">=1.0.0"
  config {
    layout = "us"
  }
}

device "pc-main" {
  type = "computer"
  capabilities = ["keyboard", "mouse"]
}

pipeline "test-pipeline" {
  source = "pc-main"
  
  step "capture" {
    device = "keyboard"
  }
}
"""


@pytest.fixture
def star_content():
    """Sample Starlark content for testing"""
    return """
VERSION = "1.0"

keyboard_ext = extension(
    name = "keyboard",
    version = ">=1.0.0",
    config = {
        "layout": "us"
    }
)

pc_main = device(
    id = "pc-main",
    type = "computer",
    capabilities = ["keyboard", "mouse"]
)

test_pipeline = pipeline(
    name = "test-pipeline",
    source = pc_main.id,
    steps = [
        step("capture", device="keyboard"),
    ]
)
"""


@pytest.fixture
def simple_content():
    """Sample Simple DSL content for testing"""
    return """
version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us"}

# Define devices
device pc-main type=computer with keyboard,mouse

# Define pipelines
pipeline test-pipeline from pc-main:
  capture keyboard
end
"""


class TestYAMLParser:
    def test_parse_yaml(self, yaml_content):
        """Test YAML parsing"""
        parser = YAMLParser()
        config = parser.parse(yaml_content)

        assert config["version"] == "1.0"
        assert len(config["extensions"]) == 1
        assert config["extensions"][0].name == "keyboard"
        assert len(config["devices"]) == 1
        assert config["devices"][0].id == "pc-main"
        assert len(config["pipelines"]) == 1
        assert config["pipelines"][0].name == "test-pipeline"

    def test_to_string(self, sample_config):
        """Test YAML serialization"""
        parser = YAMLParser()
        yaml_str = parser.to_string(sample_config)

        # Parse the generated YAML to verify it's valid
        data = yaml.safe_load(yaml_str)
        assert data["version"] == "1.0"


class TestHCLParser:
    def test_parse_hcl(self, hcl_content):
        """Test HCL parsing"""
        try:
            import hcl2
        except ImportError:
            pytest.skip("python-hcl2 not installed")

        parser = HCLParser()
        config = parser.parse(hcl_content)

        assert len(config["extensions"]) == 1
        assert config["extensions"][0].name == "keyboard"
        assert len(config["devices"]) == 1
        assert config["devices"][0].id == "pc-main"
        assert len(config["pipelines"]) == 1
        assert config["pipelines"][0].name == "test-pipeline"

    def test_to_string(self, sample_config):
        """Test HCL serialization"""
        try:
            import hcl2
        except ImportError:
            pytest.skip("python-hcl2 not installed")

        parser = HCLParser()
        hcl_str = parser.to_string(sample_config)

        # Verify the string contains expected content
        assert 'version = "1.0"' in hcl_str
        assert 'extension "keyboard"' in hcl_str
        assert 'device "pc-main"' in hcl_str
        assert 'pipeline "test-pipeline"' in hcl_str


class TestStarlarkParser:
    def test_parse_starlark(self, star_content):
        """Test Starlark parsing"""
        try:
            import starlark
        except ImportError:
            pytest.skip("starlark not installed")

        parser = StarlarkParser()
        config = parser.parse(star_content)

        assert len(config["extensions"]) == 1
        assert config["extensions"][0].name == "keyboard"
        assert len(config["devices"]) == 1
        assert config["devices"][0].id == "pc-main"
        assert len(config["pipelines"]) == 1
        assert config["pipelines"][0].name == "test-pipeline"

    def test_to_string(self, sample_config):
        """Test Starlark serialization"""
        try:
            import starlark
        except ImportError:
            pytest.skip("starlark not installed")

        parser = StarlarkParser()
        star_str = parser.to_string(sample_config)

        # Verify the string contains expected content
        assert 'VERSION = "1.0"' in star_str
        assert "keyboard_ext = extension(" in star_str
        assert "pc_main = device(" in star_str
        assert "test_pipeline = pipeline(" in star_str


class TestSimpleDSLParser:
    def test_parse_simple_dsl(self, simple_content):
        """Test Simple DSL parsing"""
        parser = SimpleDSLParser()
        config = parser.parse(simple_content)

        assert len(config["extensions"]) == 1
        assert config["extensions"][0].name == "keyboard"
        assert len(config["devices"]) == 1
        assert config["devices"][0].id == "pc-main"
        assert len(config["pipelines"]) == 1
        assert config["pipelines"][0].name == "test-pipeline"

    def test_to_string(self, sample_config):
        """Test Simple DSL serialization"""
        parser = SimpleDSLParser()
        simple_str = parser.to_string(sample_config)

        # Verify the string contains expected content
        assert 'version "1.0"' in simple_str
        assert "load keyboard" in simple_str
        assert "device pc-main" in simple_str
        assert "pipeline test-pipeline" in simple_str


class TestConfigLoader:
    def test_load_from_string(self, yaml_content):
        """Test loading from string"""
        config = ConfigLoader.load_from_string(yaml_content, "yaml")

        assert config["version"] == "1.0"
        assert len(config["extensions"]) == 1
        assert len(config["devices"]) == 1
        assert len(config["pipelines"]) == 1

    def test_convert(self, sample_config):
        """Test converting between formats"""
        yaml_str = ConfigLoader.convert(sample_config, "yaml")
        hcl_str = ConfigLoader.convert(sample_config, "hcl")
        star_str = ConfigLoader.convert(sample_config, "star")
        simple_str = ConfigLoader.convert(sample_config, "ua")

        # Verify the strings contain expected content
        assert "version:" in yaml_str or 'version: "1.0"' in yaml_str
        assert 'version = "1.0"' in hcl_str
        assert 'VERSION = "1.0"' in star_str
        assert 'version "1.0"' in simple_str

    def test_load_and_save_file(self, yaml_content):
        """Test loading and saving files"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            f.write(yaml_content.encode("utf-8"))
            yaml_file = f.name

        try:
            # Load the file
            config = ConfigLoader.load(yaml_file)

            assert config["version"] == "1.0"
            assert len(config["extensions"]) == 1
            assert len(config["devices"]) == 1
            assert len(config["pipelines"]) == 1

            # Convert to HCL and save
            with tempfile.NamedTemporaryFile(suffix=".hcl", delete=False) as f:
                hcl_file = f.name

            try:
                ConfigLoader.convert_file(yaml_file, "hcl", hcl_file)

                # Load the HCL file
                hcl_config = ConfigLoader.load(hcl_file)

                assert hcl_config["version"] == "1.0"
                assert len(hcl_config["extensions"]) == 1
                assert len(hcl_config["devices"]) == 1
                assert len(hcl_config["pipelines"]) == 1
            finally:
                os.unlink(hcl_file)
        finally:
            os.unlink(yaml_file)

    def test_unsupported_format(self):
        """Test unsupported format"""
        with pytest.raises(ValueError, match="Unsupported configuration format"):
            ConfigLoader.load_from_string("content", "invalid")


class TestSchemaValidation:
    def test_valid_config(self, sample_config):
        """Test valid configuration"""
        assert validate_config(sample_config) is True
        is_valid, error = validate_config_with_details(sample_config)
        assert is_valid is True
        assert error is None

    def test_invalid_version(self, sample_config):
        """Test invalid version"""
        sample_config["version"] = "999.0"
        assert validate_config(sample_config) is False
        is_valid, error = validate_config_with_details(sample_config)
        assert is_valid is False
        assert "version" in error.lower()

    def test_invalid_device_id(self, sample_config):
        """Test invalid device ID"""
        sample_config["devices"][0].id = "invalid id with spaces"
        assert validate_config(sample_config) is False
        is_valid, error = validate_config_with_details(sample_config)
        assert is_valid is False
        assert "id" in error.lower()
