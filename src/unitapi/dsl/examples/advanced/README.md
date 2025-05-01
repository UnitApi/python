# Advanced UnitAPI DSL Examples

This directory contains advanced examples demonstrating the power and flexibility of the UnitAPI DSL system. These examples show how to use multiple configuration formats together, create dynamic configurations, and leverage the full capabilities of the DSL system.

## Multi-Format Example

The `multi_format_example.py` script demonstrates how to combine configurations from multiple formats:

1. **Base Configuration (YAML)**: `base_config.yaml` - Contains the core configuration including extensions and the main computer device
2. **Device Configuration (HCL)**: `devices.hcl` - Contains additional device definitions in HCL format
3. **Pipeline Configuration (Starlark)**: `pipelines.star` - Contains dynamically generated pipelines using Starlark's programming capabilities

### How It Works

The example loads and merges configurations from different formats:

```python
# Load base configuration from YAML
base_config = ConfigLoader.load("base_config.yaml")

# Load device-specific configuration from HCL
device_config = ConfigLoader.load("devices.hcl")

# Merge configurations
base_config["devices"].extend(device_config["devices"])

# Load dynamic pipeline configuration from Starlark
pipeline_config = ConfigLoader.load("pipelines.star")
base_config["pipelines"] = pipeline_config["pipelines"]

# Execute combined configuration
executor = DSLExecutor(unitapi_instance)
await executor.execute_config(base_config)
```

## Dynamic Pipeline Generation

The `pipelines.star` file demonstrates how to use Starlark's programming capabilities to dynamically generate pipelines:

1. **Helper Functions**: Define reusable functions for creating different types of pipelines
2. **Device Mapping**: Define mappings between devices and their capabilities
3. **Dynamic Generation**: Generate pipelines based on device capabilities and relationships
4. **Conditional Logic**: Add or modify pipelines based on environment (development, testing, production)

### Example of Dynamic Generation

```python
# Generate monitoring pipelines
monitoring_pipelines = []
for source, sensor_types in sensor_devices.items():
    target = monitoring_targets.get(source, "pc-main")
    for sensor_type in sensor_types:
        # Set different thresholds based on sensor type
        if sensor_type == "temperature":
            threshold = 75 if ENVIRONMENT == "production" else 85
        elif sensor_type == "motion":
            threshold = 0.7
        else:
            threshold = 50
        
        # Create and add the pipeline
        monitoring_pipelines.append(
            create_monitoring_pipeline(source, target, sensor_type, threshold)
        )
```

## Benefits of Multi-Format Approach

This approach offers several benefits:

1. **Separation of Concerns**: Keep different aspects of configuration in different files
2. **Format Flexibility**: Use the most appropriate format for each part of the configuration
3. **Reusability**: Share common configurations across multiple projects
4. **Dynamic Generation**: Generate complex configurations programmatically
5. **Environment-Specific Configuration**: Adapt configuration based on environment

## Running the Example

To run the multi-format example:

```bash
# Install required dependencies
pip install pyyaml python-hcl2 starlark pydantic

# Run the example
python -m unitapi.dsl.examples.advanced.multi_format_example
```

## Extending the Example

You can extend this example in several ways:

1. **Add More Formats**: Add configurations in other formats (e.g., Simple DSL)
2. **Add More Devices**: Add more devices to the HCL configuration
3. **Add More Pipelines**: Add more pipeline generation logic to the Starlark configuration
4. **Add More Event Handlers**: Add more event handlers to respond to state changes
5. **Add More Environment-Specific Logic**: Add more environment-specific configuration

## Real-World Use Cases

This approach is particularly useful for:

1. **IoT Systems**: Configure complex networks of IoT devices
2. **Distributed Systems**: Configure distributed systems with many components
3. **Multi-Environment Deployments**: Configure systems for different environments
4. **Dynamic Systems**: Configure systems that change frequently
5. **Complex Workflows**: Configure complex workflows with many steps
