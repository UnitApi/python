# YAML Configuration Format for UnitAPI DSL

YAML (YAML Ain't Markup Language) is a human-readable data serialization standard that's easy to write and understand. It's a popular choice for configuration files due to its clean syntax and readability.

## Features

- Human-readable format with minimal syntax
- Uses indentation to represent structure
- Supports comments with `#`
- Uses custom tags (`!extension`, `!device`, `!pipeline`) for type identification
- Good for simple configurations and readability

## Example

This directory contains an example YAML configuration for UnitAPI DSL:

- `example.yaml` - Camera device configuration demonstrating YAML syntax

## Structure

A typical YAML configuration for UnitAPI includes:

1. **Version** - The version of the configuration format
2. **Extensions** - Definitions of device capabilities and requirements
3. **Devices** - Definitions of physical or virtual hardware
4. **Pipelines** - Workflows that connect devices and process data

## Testing

You can test the YAML configuration using the provided `test.py` script:

```bash
# Run the test script
python test.py

# Test with a different configuration file
python test.py --config other_config.yaml

# Validate without executing
python test.py --dry-run

# Convert to another format
python test.py --convert-to hcl
```

## When to Use YAML

YAML is a good choice when:

- You want a configuration format that's easy to read and write
- Your configuration is relatively simple
- You prefer a minimal syntax with less punctuation
- You want to include comments to explain your configuration

## Learn More

For more information about UnitAPI DSL and its supported formats, see the main [DSL documentation](../../../docs/dsl.md).
