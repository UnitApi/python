import pytest
import os
import glob
from pathlib import Path

from unitapi.config.loader import ConfigLoader
from unitapi.dsl.validators.schema import validate_config, validate_config_with_details

# Get all example files
EXAMPLES_DIR = Path("examples/dsl")
YAML_EXAMPLES = list(EXAMPLES_DIR.glob("*.yaml"))
HCL_EXAMPLES = list(EXAMPLES_DIR.glob("*.hcl"))
STAR_EXAMPLES = list(EXAMPLES_DIR.glob("*.star"))
SIMPLE_EXAMPLES = list(EXAMPLES_DIR.glob("*.ua"))

ALL_EXAMPLES = YAML_EXAMPLES + HCL_EXAMPLES + STAR_EXAMPLES + SIMPLE_EXAMPLES

@pytest.mark.parametrize("example_path", ALL_EXAMPLES)
def test_example_loads(example_path):
    """Test that all example files can be loaded"""
    try:
        config = ConfigLoader.load(str(example_path))
        assert config is not None
        assert "version" in config
        assert "extensions" in config
        assert "devices" in config
        assert "pipelines" in config
    except Exception as e:
        pytest.fail(f"Failed to load {example_path}: {e}")

@pytest.mark.parametrize("example_path", ALL_EXAMPLES)
def test_example_validates(example_path):
    """Test that all example files validate against the schema"""
    try:
        config = ConfigLoader.load(str(example_path))
        is_valid, error = validate_config_with_details(config)
        assert is_valid, f"Validation failed for {example_path}: {error}"
    except Exception as e:
        pytest.fail(f"Failed to validate {example_path}: {e}")

@pytest.mark.parametrize("example_path", ALL_EXAMPLES)
def test_example_devices_have_required_fields(example_path):
    """Test that all devices in examples have required fields"""
    try:
        config = ConfigLoader.load(str(example_path))
        for device in config.get("devices", []):
            assert device.id, f"Device in {example_path} missing id"
            assert device.device_type, f"Device in {example_path} missing device_type"
            assert isinstance(device.capabilities, list), f"Device in {example_path} has invalid capabilities"
    except Exception as e:
        pytest.fail(f"Failed to check device fields in {example_path}: {e}")

@pytest.mark.parametrize("example_path", ALL_EXAMPLES)
def test_example_pipelines_have_required_fields(example_path):
    """Test that all pipelines in examples have required fields"""
    try:
        config = ConfigLoader.load(str(example_path))
        for pipeline in config.get("pipelines", []):
            assert pipeline.name, f"Pipeline in {example_path} missing name"
            assert isinstance(pipeline.steps, list), f"Pipeline in {example_path} has invalid steps"
            
            # Check that all steps have an action
            for step in pipeline.steps:
                assert step.action, f"Step in pipeline {pipeline.name} in {example_path} missing action"
    except Exception as e:
        pytest.fail(f"Failed to check pipeline fields in {example_path}: {e}")

@pytest.mark.parametrize("example_path", ALL_EXAMPLES)
def test_example_extensions_have_required_fields(example_path):
    """Test that all extensions in examples have required fields"""
    try:
        config = ConfigLoader.load(str(example_path))
        for extension in config.get("extensions", []):
            assert extension.name, f"Extension in {example_path} missing name"
            assert extension.version, f"Extension in {example_path} missing version"
    except Exception as e:
        pytest.fail(f"Failed to check extension fields in {example_path}: {e}")

def test_format_conversion():
    """Test that examples can be converted between formats"""
    # Test conversion from each format to all other formats
    for source_path in ALL_EXAMPLES[:1]:  # Just test the first example for speed
        try:
            config = ConfigLoader.load(str(source_path))
            
            # Convert to each format
            yaml_str = ConfigLoader.convert(config, "yaml")
            hcl_str = ConfigLoader.convert(config, "hcl")
            star_str = ConfigLoader.convert(config, "star")
            simple_str = ConfigLoader.convert(config, "ua")
            
            # Verify the converted strings contain expected content
            assert "version" in yaml_str.lower()
            assert "version" in hcl_str.lower()
            assert "version" in star_str.lower()
            assert "version" in simple_str.lower()
            
            # Verify the converted strings can be loaded back
            yaml_config = ConfigLoader.load_from_string(yaml_str, "yaml")
            hcl_config = ConfigLoader.load_from_string(hcl_str, "hcl")
            star_config = ConfigLoader.load_from_string(star_str, "star")
            simple_config = ConfigLoader.load_from_string(simple_str, "ua")
            
            # Verify the loaded configs have the expected structure
            for cfg in [yaml_config, hcl_config, star_config, simple_config]:
                assert "version" in cfg
                assert "extensions" in cfg
                assert "devices" in cfg
                assert "pipelines" in cfg
        except Exception as e:
            pytest.fail(f"Failed to convert {source_path}: {e}")

def test_multi_device_examples():
    """Test that multi-device examples have devices referenced in pipelines"""
    multi_device_examples = [
        p for p in ALL_EXAMPLES 
        if "multi" in p.name.lower() or "workflow" in p.name.lower()
    ]
    
    for example_path in multi_device_examples:
        try:
            config = ConfigLoader.load(str(example_path))
            
            # Get all device IDs
            device_ids = [device.id for device in config.get("devices", [])]
            
            # Check that pipelines reference existing devices
            for pipeline in config.get("pipelines", []):
                if pipeline.source:
                    # Source can be a single device or a list of devices
                    if isinstance(pipeline.source, list):
                        for source in pipeline.source:
                            assert source in device_ids, f"Pipeline {pipeline.name} references non-existent source device {source}"
                    else:
                        assert pipeline.source in device_ids, f"Pipeline {pipeline.name} references non-existent source device {pipeline.source}"
                
                if pipeline.target:
                    # Target can be a single device or a list of devices
                    if isinstance(pipeline.target, list):
                        for target in pipeline.target:
                            assert target in device_ids, f"Pipeline {pipeline.name} references non-existent target device {target}"
                    else:
                        assert pipeline.target in device_ids, f"Pipeline {pipeline.name} references non-existent target device {pipeline.target}"
        except Exception as e:
            pytest.fail(f"Failed to check multi-device example {example_path}: {e}")

def test_device_type_coverage():
    """Test that examples cover all major device types"""
    # List of device types we want to ensure are covered
    device_types = [
        "camera", "microphone", "speaker", "keyboard", "mouse", 
        "touchscreen", "gamepad", "gpio"
    ]
    
    covered_types = set()
    
    for example_path in ALL_EXAMPLES:
        try:
            config = ConfigLoader.load(str(example_path))
            for device in config.get("devices", []):
                device_type = device.device_type.lower()
                for dt in device_types:
                    if dt in device_type:
                        covered_types.add(dt)
        except Exception:
            continue
    
    # Check that all device types are covered
    for dt in device_types:
        assert dt in covered_types, f"Device type {dt} not covered in any example"

if __name__ == "__main__":
    # Run tests manually
    for example_path in ALL_EXAMPLES:
        print(f"Testing {example_path}...")
        test_example_loads(example_path)
        test_example_validates(example_path)
        test_example_devices_have_required_fields(example_path)
        test_example_pipelines_have_required_fields(example_path)
        test_example_extensions_have_required_fields(example_path)
    
    print("Testing format conversion...")
    test_format_conversion()
    
    print("Testing multi-device examples...")
    test_multi_device_examples()
    
    print("Testing device type coverage...")
    test_device_type_coverage()
    
    print("All tests passed!")
