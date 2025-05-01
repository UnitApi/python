# Simple UA Configuration Format for UnitAPI DSL

The Simple UA (UnitAPI) format is a custom, shell-like syntax designed specifically for UnitAPI. It provides a concise and intuitive way to define device configurations and workflows.

## Features

- Custom syntax designed specifically for UnitAPI
- Concise and easy to read
- Good for quick configurations and scripting
- Uses a shell-like syntax with commands and blocks
- Minimal punctuation and clear structure

## Example

This directory contains an example Simple UA configuration for UnitAPI DSL:

- `example.ua` - Input devices configuration demonstrating Simple UA syntax

## Structure

A typical Simple UA configuration for UnitAPI includes:

1. **Version** - The version of the configuration format
2. **Extensions** - Loaded using the `load` command
3. **Devices** - Defined using the `device` command
4. **Pipelines** - Defined using the `pipeline` command with blocks

## Testing

You can test the Simple UA configuration using the provided `test.py` script:

```bash
# Run the test script
python test.py

# Test with a different configuration file
python test.py --config other_config.ua

# Validate without executing
python test.py --dry-run

# Convert to another format
python test.py --convert-to yaml

# List all devices in the configuration
python test.py --list-devices
```

## When to Use Simple UA

Simple UA is a good choice when:

- You want a configuration format that's quick to write
- You prefer a command-line-like syntax
- You need a format that's easy to generate programmatically
- You want a format that's specific to UnitAPI
- You need a concise way to define device configurations and workflows

## Syntax Highlights

```
# This is a comment

version "1.0"

# Load extensions
load device_type version=">=1.0.0" config={param1:value1, param2:value2}

# Define devices
device device-id type=device_type with capability1,capability2,capability3

# Define pipelines
pipeline pipeline-name from device-id:
  capture events
  filter criteria=value
  process operation=true
  execute action="command"
end

# Define pipelines with source and target
pipeline pipeline-name from source-device to target-device:
  capture events
  process operation=true
  forward destination="endpoint"
end

# Define event handlers
pipeline combined-input from device1,device2:
  capture all_events
  on device1.event=value:execute action="command1"
  on device2.event=value:execute action="command2"
end
```

## Learn More

For more information about UnitAPI DSL and its supported formats, see the main [DSL documentation](../../../docs/dsl.md).
