# UnitAPI DSL (Domain Specific Language)

UnitAPI provides multiple configuration formats for defining device setups, extensions, and pipelines. This flexibility allows users to choose the format that best suits their needs.

## Supported Formats

1. **YAML** (.yaml, .yml) - Human-readable with custom tags
2. **HCL** (.hcl) - HashiCorp Configuration Language
3. **Starlark** (.star) - Python-like scripting
4. **Simple DSL** (.ua) - Shell-like commands

## Quick Start

### Installation

To use the DSL module, you need to install the required dependencies:

```bash
# Install core dependencies
pip install pyyaml pydantic

# Install format-specific dependencies (optional)
pip install python-hcl2  # For HCL format
pip install starlark     # For Starlark format
```

You can also use the built-in command to install dependencies:

```bash
unitapi dsl deps --install
```

### Creating a Configuration

You can create a new configuration file using the template command:

```bash
unitapi dsl template yaml > config.yaml
unitapi dsl template hcl > config.hcl
unitapi dsl template star > config.star
unitapi dsl template ua > config.ua
```

Or use the init command to create a new configuration file:

```bash
unitapi dsl init --format yaml --output config.yaml
```

### Running a Configuration

To run a configuration file:

```bash
unitapi dsl run config.yaml
```

You can also validate a configuration file without running it:

```bash
unitapi dsl validate config.yaml
```

### Converting Between Formats

You can convert between formats:

```bash
unitapi dsl convert config.yaml hcl --output config.hcl
```

## Configuration Structure

All configuration formats share the same basic structure:

1. **Version** - The configuration version
2. **Extensions** - Extensions to load
3. **Devices** - Devices to initialize
4. **Pipelines** - Pipelines to run

### YAML Example

```yaml
version: "1.0"

extensions:
  - !extension
    name: keyboard
    version: ">=1.0.0"
    config:
      layout: "us"
      
  - !extension
    name: mouse
    version: ">=1.0.0"
    config:
      sensitivity: 1.5

devices:
  - !device
    id: "pc-main"
    device_type: "computer"
    capabilities: ["keyboard", "mouse", "display"]
    
  - !device
    id: "rpi-remote"
    device_type: "raspberry_pi"
    capabilities: ["gpio", "camera"]

pipelines:
  - !pipeline
    name: "remote-control"
    source: "pc-main"
    target: "rpi-remote"
    steps:
      - action: "capture"
        params:
          device: "keyboard"
      - action: "filter"
        params:
          keys: ["ctrl", "alt", "f1-f12"]
      - action: "forward"
        params:
          destination: "tcp://192.168.1.100:5000"
```

### HCL Example

```hcl
version = "1.0"

extension "keyboard" {
  version = ">=1.0.0"
  config {
    layout = "us"
  }
}

extension "mouse" {
  version = ">=1.0.0"
  config {
    sensitivity = 1.5
  }
}

device "pc-main" {
  type = "computer"
  capabilities = ["keyboard", "mouse", "display"]
}

device "rpi-remote" {
  type = "raspberry_pi"
  capabilities = ["gpio", "camera"]
}

pipeline "remote-control" {
  source = "pc-main"
  target = "rpi-remote"
  
  step "capture" {
    device = "keyboard"
  }
  
  step "filter" {
    keys = ["ctrl", "alt", "f1-f12"]
  }
  
  step "forward" {
    destination = "tcp://192.168.1.100:5000"
  }
}
```

### Starlark Example

```python
VERSION = "1.0"

keyboard_ext = extension(
    name = "keyboard",
    version = ">=1.0.0",
    config = {
        "layout": "us"
    }
)

mouse_ext = extension(
    name = "mouse",
    version = ">=1.0.0",
    config = {
        "sensitivity": 1.5
    }
)

pc_main = device(
    id = "pc-main",
    type = "computer",
    capabilities = ["keyboard", "mouse", "display"]
)

rpi_remote = device(
    id = "rpi-remote",
    type = "raspberry_pi",
    capabilities = ["gpio", "camera"]
)

remote_control = pipeline(
    name = "remote-control",
    source = pc_main.id,  # Reference device ID
    target = rpi_remote.id,
    steps = [
        step("capture", device="keyboard"),
        step("filter", keys=["ctrl", "alt", "f1-f12"]),
        step("forward", destination="tcp://192.168.1.100:5000")
    ]
)
```

### Simple DSL Example

```bash
version "1.0"

# Load extensions
load keyboard version=">=1.0.0" config={layout:"us"}
load mouse version=">=1.0.0" config={sensitivity:1.5}

# Define devices
device pc-main type=computer with keyboard,mouse,display
device rpi-remote type=raspberry_pi with gpio,camera

# Define pipelines
pipeline remote-control from pc-main to rpi-remote:
  capture keyboard
  filter ctrl,alt,f1-f12
  forward destination="tcp://192.168.1.100:5000"
end
```

## CLI Commands

UnitAPI DSL provides several CLI commands:

### Run

Run a configuration file:

```bash
unitapi dsl run config.yaml
```

Options:
- `--dry-run`: Validate without executing
- `--verbose`, `-v`: Enable verbose output

### Validate

Validate a configuration file:

```bash
unitapi dsl validate config.yaml
```

Options:
- `--verbose`, `-v`: Enable verbose output

### Convert

Convert between formats:

```bash
unitapi dsl convert config.yaml hcl --output config.hcl
```

Options:
- `--output`, `-o`: Output file (default: stdout)
- `--verbose`, `-v`: Enable verbose output

### Template

Generate a template configuration:

```bash
unitapi dsl template yaml
```

Options:
- `--output`, `-o`: Output file (default: stdout)

### Init

Initialize a new configuration file:

```bash
unitapi dsl init --format yaml
```

Options:
- `--format`, `-f`: Format to use (default: yaml)
- `--output`, `-o`: Output file (default: unitapi.{format})

### Dependencies

Manage DSL dependencies:

```bash
unitapi dsl deps --list
unitapi dsl deps --install
```

Options:
- `--list`: List required dependencies
- `--install`: Install required dependencies

### Info

Display information about a configuration file:

```bash
unitapi dsl info config.yaml
```

Options:
- `--format`, `-f`: Output format (default: yaml)

## Programmatic Usage

You can also use the DSL module programmatically:

```python
from unitapi.config.loader import ConfigLoader
from unitapi.dsl.runtime.executor import DSLExecutor
from unitapi import UnitAPI

# Load configuration
config = ConfigLoader.load("config.yaml")

# Initialize UnitAPI
unitapi = UnitAPI()

# Set up executor
executor = DSLExecutor(unitapi)

# Run configuration
async def run_async():
    await executor.execute_config(config)
    
    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await executor.stop_all()
        await executor.cleanup()

asyncio.run(run_async())
```

## Format Comparison

### YAML

- **Advantages**: Most readable, supports custom tags for type safety
- **Custom Tags**: `!extension`, `!device`, `!pipeline`
- **Best For**: Human-edited configurations

### HCL (HashiCorp Configuration Language)

- **Advantages**: Clean syntax, good for infrastructure as code
- **Features**: Blocks and attributes, expressions
- **Best For**: DevOps workflows

### Starlark

- **Advantages**: Python-like syntax, supports logic and variables
- **Features**: Functions, conditionals, loops
- **Best For**: Complex configurations with dynamic logic

### Simple DSL

- **Advantages**: Shell-like syntax, very easy to learn
- **Features**: Simple commands, minimal syntax
- **Best For**: Non-technical users, quick configurations

## Advanced Features

### Variable Substitution (Starlark)

```python
base_config = {
    "layout": "us"
}

keyboard_ext = extension(
    name = "keyboard",
    config = base_config
)
```

### Conditional Configuration (Starlark)

```python
if environment == "production":
    pipeline_config = production_pipeline()
else:
    pipeline_config = development_pipeline()
```

### Dynamic Pipeline Generation (Starlark)

```python
def create_monitoring_pipeline(device_id, threshold):
    """Create a monitoring pipeline with the given threshold"""
    return pipeline(
        name = f"monitor-{device_id}",
        source = device_id,
        steps = [
            step("read", sensor="temperature"),
            step("filter", threshold=threshold),
            # Conditional step based on threshold
            step("alert", method="email") if threshold > 80 else step("log")
        ]
    )

# Create monitoring pipelines for multiple devices
devices = ["sensor1", "sensor2", "sensor3"]
thresholds = [75, 80, 85]

for i, device_id in enumerate(devices):
    monitoring_pipeline = create_monitoring_pipeline(device_id, thresholds[i])
```

## Best Practices

1. Use YAML for hand-edited configurations
2. Use HCL for infrastructure-as-code workflows
3. Use Starlark when you need logic and variables
4. Use Simple DSL for quick scripts and non-technical users
5. Always validate configurations before deployment
6. Use version control for configuration files
7. Document custom extensions and pipeline steps
