# UnitAPI DSL Module

The UnitAPI DSL (Domain Specific Language) module provides a flexible and powerful way to configure and control UnitAPI systems using various configuration formats. This module allows users to define devices, extensions, and pipelines in a declarative way, making it easier to set up and manage complex UnitAPI deployments.

## Features

- **Multiple Configuration Formats**: Support for YAML, HCL, Starlark, and a custom Simple DSL format
- **Validation**: Schema validation to ensure configuration correctness
- **CLI Commands**: Command-line interface for running, validating, and converting configurations
- **Programmatic API**: API for using the DSL module in Python code
- **Dynamic Configuration**: Support for dynamic configuration generation using Starlark
- **Format Conversion**: Convert between different configuration formats

## Directory Structure

```
unitapi/dsl/
├── __init__.py
├── base.py              # Base classes for DSL
├── parsers/
│   ├── __init__.py
│   ├── yaml_parser.py   # YAML parser with custom tags
│   ├── hcl_parser.py    # HCL parser
│   ├── starlark_parser.py # Starlark parser
│   └── simple_parser.py # Simple DSL parser
├── validators/
│   ├── __init__.py
│   └── schema.py        # Schema validators
├── runtime/
│   ├── __init__.py
│   ├── executor.py      # DSL executor
│   └── context.py       # Execution context
└── examples/            # Examples for each format
    ├── simple.ua
    ├── config.yaml
    ├── config.hcl
    ├── config.star
    └── advanced/        # Advanced examples
```

## Installation

The DSL module is included in the UnitAPI package. To install the required dependencies:

```bash
# Install core dependencies
pip install pyyaml pydantic click

# Install format-specific dependencies (optional)
pip install python-hcl2 starlark
```

You can also use the built-in command to install dependencies:

```bash
unitapi dsl deps --install
```

## Usage

### Command Line Interface

The DSL module provides a command-line interface for working with configurations:

```bash
# Run a configuration
unitapi dsl run config.yaml

# Validate a configuration
unitapi dsl validate config.yaml

# Convert between formats
unitapi dsl convert config.yaml hcl --output config.hcl

# Generate a template
unitapi dsl template yaml > config.yaml

# Initialize a new configuration
unitapi dsl init --format yaml

# Display information about a configuration
unitapi dsl info config.yaml
```

### Programmatic API

You can also use the DSL module programmatically:

```python
from unitapi import UnitAPI
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.runtime.executor import DSLExecutor

# Load configuration
config = ConfigLoader.load("config.yaml")

# Initialize UnitAPI
unitapi = UnitAPI()

# Set up executor
executor = DSLExecutor(unitapi)

# Execute configuration
await executor.execute_config(config)
```

## Configuration Formats

### YAML

```yaml
version: "1.0"

extensions:
  - name: keyboard
    type: extension
    version: ">=1.0.0"
    config:
      layout: "us"

devices:
  - id: "pc-main"
    type: device
    device_type: "computer"
    capabilities: ["keyboard", "mouse", "display"]

pipelines:
  - name: "remote-control"
    type: pipeline
    source: "pc-main"
    steps:
      - action: "capture"
        type: step
        params:
          device: "keyboard"
```

### HCL

```hcl
version = "1.0"

extension "keyboard" {
  version = ">=1.0.0"
  config {
    layout = "us"
  }
}

device "pc-main" {
  type = "computer"
  capabilities = ["keyboard", "mouse", "display"]
}

pipeline "remote-control" {
  source = "pc-main"
  
  step "capture" {
    device = "keyboard"
  }
}
```

### Starlark

```python
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
    capabilities = ["keyboard", "mouse", "display"]
)

remote_control = pipeline(
    name = "remote-control",
    source = pc_main.id,
    steps = [
        step("capture", device="keyboard"),
    ]
)
```

### Simple DSL

```
version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us"}

# Define devices
device pc-main type=computer with keyboard,mouse,display

# Define pipelines
pipeline remote-control from pc-main:
  capture keyboard
end
```

## Advanced Usage

See the [advanced examples](examples/advanced/) for more complex usage scenarios, including:

- Multi-format configurations
- Dynamic pipeline generation
- Environment-specific configurations
- Event handling

## Documentation

For more detailed documentation, see the [DSL documentation](../../../docs/dsl.md).

## Contributing

Contributions to the DSL module are welcome! Please follow the UnitAPI contribution guidelines.
