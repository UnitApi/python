# UnitAPI DSL Examples

This directory contains example configurations for the UnitAPI Domain Specific Language (DSL) in various formats. These examples demonstrate how to configure and control different types of devices and create workflows that connect multiple devices together.

## Available Formats

UnitAPI DSL supports multiple configuration formats to suit different preferences and use cases. Each format has its own dedicated directory with examples and documentation:

1. [**YAML**](yaml/) (`.yaml`) - A human-readable data serialization standard that's easy to write and understand
2. [**HCL**](hcl/) (`.hcl`) - HashiCorp Configuration Language, offering a more structured and expressive syntax
3. [**Starlark**](star/) (`.star`) - A Python-like configuration language that supports functions and more complex logic
4. [**Simple DSL**](ua/) (`.ua`) - A custom, shell-like syntax designed specifically for UnitAPI
5. [**JSON**](json/) (`.json`) - A standard, language-independent data format widely used for configuration files and APIs

## Directory Structure

Each format has its own directory containing:

- `README.md` - Documentation specific to that format
- `example.*` - An example configuration file in that format
- `test.py` - A test script to validate and execute the example configuration

## Format Comparison

| Format | Strengths | Best For |
|--------|-----------|----------|
| YAML | Human-readable, minimal syntax | Simple configurations, readability |
| HCL | Structured, supports comments | Complex nested structures |
| Starlark | Python-like, supports functions | Dynamic configurations, reusable components |
| Simple UA | Concise, shell-like syntax | Quick configurations, scripting |
| JSON | Standard, widely supported | Machine-generated configurations, interoperability |

## Key Concepts

### Extensions

Extensions define the capabilities and requirements for specific device types. They include:

- Name and version
- Configuration parameters specific to the device type

### Devices

Devices represent physical or virtual hardware that can be controlled by UnitAPI. They include:

- Unique ID
- Device type
- Capabilities list

### Pipelines

Pipelines define workflows that connect devices and process data. They include:

- Name
- Source device(s)
- Target device(s)
- Processing steps

## Testing

Each format directory contains a `test.py` script that can be used to test the example configuration:

```bash
# Navigate to a format directory
cd yaml

# Run the test script
python test.py

# Test with a different configuration file
python test.py --config other_config.yaml

# Validate without executing
python test.py --dry-run

# Convert to another format
python test.py --convert-to hcl
```

## Usage

To use these examples in your own code:

```python
from unitapi.config.loader import ConfigLoader
from unitapi import UnitAPI
from unitapi.dsl.runtime.executor import DSLExecutor

# Load a configuration file
config = ConfigLoader.load("examples/dsl/yaml/example.yaml")

# Use the configuration with UnitAPI
unitapi = UnitAPI()
executor = DSLExecutor(unitapi)
await executor.execute_config(config)
```

## Additional Resources

- [UnitAPI Documentation](../../docs/index.md)
- [DSL Documentation](../../docs/dsl.md)
- [Device Types Documentation](../../docs/device_types.md)
