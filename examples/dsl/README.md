# UnitAPI DSL Examples

This directory contains example configurations for the UnitAPI Domain Specific Language (DSL) in various formats. These examples demonstrate how to configure and control different types of devices and create workflows that connect multiple devices together.

## Available Formats

UnitAPI DSL supports multiple configuration formats to suit different preferences and use cases:

1. **YAML** (`.yaml`) - A human-readable data serialization standard that's easy to write and understand
2. **HCL** (`.hcl`) - HashiCorp Configuration Language, offering a more structured and expressive syntax
3. **Starlark** (`.star`) - A Python-like configuration language that supports functions and more complex logic
4. **Simple DSL** (`.ua`) - A custom, shell-like syntax designed specifically for UnitAPI

## Example Files

### Device-Specific Examples

Each example focuses on a specific device type and demonstrates its capabilities:

- `camera_config.yaml` - Camera device configuration in YAML format
- `microphone_config.hcl` - Microphone device configuration in HCL format
- `speaker_config.star` - Speaker device configuration in Starlark format
- `input_devices.ua` - Keyboard and mouse configuration in Simple DSL format
- `touch_gamepad_config.yaml` - Touchscreen and gamepad configuration in YAML format
- `gpio_config.hcl` - GPIO device configuration in HCL format

### Multi-Device Workflows

These examples demonstrate how to create workflows that connect multiple devices:

- `multi_device_workflow.star` - Complex multi-device workflow in Starlark format
- `multi_device_simple.ua` - Multi-device workflow in Simple DSL format

## Test Files

This directory includes Python scripts to test and demonstrate the usage of different configuration formats:

- `test_yaml_config.py` - Test script for YAML configuration files
- `test_hcl_config.py` - Test script for HCL configuration files
- `test_star_config.py` - Test script for Starlark configuration files
- `test_ua_config.py` - Test script for Simple UA configuration files
- `test_multi_format.py` - Test script that demonstrates combining multiple configuration formats

### Running the Test Scripts

Each test script can be run directly from the command line:

```bash
# Test a YAML configuration
python test_yaml_config.py --config camera_config.yaml

# Test an HCL configuration
python test_hcl_config.py --config microphone_config.hcl

# Test a Starlark configuration
python test_star_config.py --config speaker_config.star

# Test a Simple UA configuration
python test_ua_config.py --config input_devices.ua

# Test combining multiple formats
python test_multi_format.py
```

### Command Line Options

Each test script supports various command line options:

- `--config` - Specify the configuration file to test (default varies by script)
- `--dry-run` - Validate the configuration without executing it
- `--convert-to` - Convert the configuration to another format (e.g., yaml, hcl, star, ua)

Additional options for specific scripts:

- `test_star_config.py` supports `--list-pipelines` to display all pipelines in the configuration
- `test_ua_config.py` supports `--list-devices` to display all devices in the configuration
- `test_multi_format.py` supports options to specify different configuration files for each component:
  - `--base-config` - Base configuration file (default: camera_config.yaml)
  - `--device-config` - Device configuration file (default: microphone_config.hcl)
  - `--pipeline-config` - Pipeline configuration file (default: speaker_config.star)
  - `--additional-config` - Additional configuration file (default: input_devices.ua)
  - `--output-format` - Format for the combined configuration output

## Key Concepts

### Extensions

Extensions define the capabilities and requirements for specific device types. They include:

- Name and version
- Configuration parameters specific to the device type

Example (YAML):
```yaml
extensions:
  - !extension
    name: camera
    version: ">=1.0.0"
    config:
      resolution: "1080p"
      fps: 30
```

### Devices

Devices represent physical or virtual hardware that can be controlled by UnitAPI. They include:

- Unique ID
- Device type
- Capabilities list

Example (HCL):
```hcl
device "rpi-gpio" {
  type = "raspberry_pi_gpio"
  capabilities = ["digital_io", "pwm", "i2c", "spi"]
}
```

### Pipelines

Pipelines define workflows that connect devices and process data. They include:

- Name
- Source device(s)
- Target device(s)
- Processing steps

Example (Starlark):
```python
video_conference = pipeline(
    name = "video-conference",
    steps = [
        step("capture", 
            sources=[pc_camera.id, pc_microphone.id],
            video_settings={"resolution": "720p", "fps": 30}
        ),
        step("process",
            video_processing={"background_blur": True}
        ),
        step("output",
            video_target={"display": "primary"},
            audio_target=pc_speaker.id
        )
    ]
)
```

## Usage

To use these examples, you can:

1. Load them directly with the UnitAPI ConfigLoader:
   ```python
   from unitapi.config.loader import ConfigLoader
   
   # Load a configuration file
   config = ConfigLoader.load("examples/dsl/camera_config.yaml")
   
   # Use the configuration with UnitAPI
   from unitapi import UnitAPI
   from unitapi.dsl.runtime.executor import DSLExecutor
   
   unitapi = UnitAPI()
   executor = DSLExecutor(unitapi)
   await executor.execute_config(config)
   ```

2. Convert between formats:
   ```python
   from unitapi.config.loader import ConfigLoader
   
   # Load a YAML configuration
   config = ConfigLoader.load("examples/dsl/camera_config.yaml")
   
   # Convert to HCL
   hcl_content = ConfigLoader.convert(config, "hcl")
   
   # Save to a file
   with open("converted_config.hcl", "w") as f:
       f.write(hcl_content)
   ```

3. Run via the command line:
   ```bash
   # Run a configuration
   unitapi dsl run examples/dsl/camera_config.yaml
   
   # Validate a configuration
   unitapi dsl validate examples/dsl/microphone_config.hcl
   
   # Convert between formats
   unitapi dsl convert examples/dsl/speaker_config.star yaml --output speaker_config.yaml
   ```

## Testing

The examples can be tested using the provided test suite:

```bash
# Run all tests
pytest tests/test_dsl_examples.py

# Run a specific test
pytest tests/test_dsl_examples.py::test_device_type_coverage
```

## Creating Your Own Configurations

To create your own configurations:

1. Choose a format that suits your needs
2. Define the extensions for the device types you'll use
3. Define your devices with unique IDs and capabilities
4. Create pipelines to connect devices and define workflows
5. Validate your configuration using `unitapi dsl validate`
6. Run your configuration using `unitapi dsl run`

## Format-Specific Tips

### YAML

- Uses custom tags (`!extension`, `!device`, `!pipeline`) for type identification
- Good for simple configurations and readability

### HCL

- More structured with blocks for each component
- Supports comments and multi-line strings
- Good for complex configurations with nested structures

### Starlark

- Python-like syntax with variables and functions
- Supports programmatic generation of configurations
- Good for dynamic configurations and reusable components

### Simple DSL

- Custom syntax designed for UnitAPI
- Concise and easy to read
- Good for quick configurations and scripting

## Additional Resources

- [UnitAPI Documentation](../../docs/index.md)
- [DSL Documentation](../../docs/dsl.md)
- [Device Types Documentation](../../docs/device_types.md)
