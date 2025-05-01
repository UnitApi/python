# HCL Configuration Format for UnitAPI DSL

HCL (HashiCorp Configuration Language) is a structured configuration language that is both human and machine-friendly. It's designed to be used for both human-authored configuration as well as machine-generated configuration.

## Features

- More structured with blocks for each component
- Supports comments and multi-line strings
- Good for complex configurations with nested structures
- Offers a balance between readability and expressiveness
- Similar to JSON but with added features like comments and block structures

## Example

This directory contains an example HCL configuration for UnitAPI DSL:

- `example.hcl` - Microphone device configuration demonstrating HCL syntax

## Structure

A typical HCL configuration for UnitAPI includes:

1. **Version** - The version of the configuration format
2. **Extensions** - Definitions of device capabilities and requirements
3. **Devices** - Definitions of physical or virtual hardware
4. **Pipelines** - Workflows that connect devices and process data

## Testing

You can test the HCL configuration using the provided `test.py` script:

```bash
# Run the test script
python test.py

# Test with a different configuration file
python test.py --config other_config.hcl

# Validate without executing
python test.py --dry-run

# Convert to another format
python test.py --convert-to yaml
```

## When to Use HCL

HCL is a good choice when:

- You need a more structured format than YAML
- Your configuration has complex nested structures
- You want to include comments to explain your configuration
- You prefer a format that's similar to programming languages
- You need to represent complex data structures with clear hierarchies

## Syntax Highlights

```hcl
# This is a comment

version = "1.0"

extension "device_type" {
  version = ">=1.0.0"
  config {
    parameter1 = value1
    parameter2 = value2
  }
}

device "device_id" {
  type = "device_type"
  capabilities = ["capability1", "capability2"]
  metadata = {
    key1 = "value1"
    key2 = "value2"
  }
}

pipeline "pipeline_name" {
  source = "device_id"
  
  step "step_name" {
    parameter1 = value1
    parameter2 = value2
  }
}
```

## Learn More

For more information about UnitAPI DSL and its supported formats, see the main [DSL documentation](../../../docs/dsl.md).
