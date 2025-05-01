# Starlark Configuration Format for UnitAPI DSL

Starlark is a Python-like configuration language that supports functions and more complex logic. It's designed to be simple, deterministic, and hermetic, making it ideal for configuration files that require more programmatic capabilities.

## Features

- Python-like syntax with variables and functions
- Supports programmatic generation of configurations
- Good for dynamic configurations and reusable components
- Allows for more complex logic and data manipulation
- Provides a familiar syntax for Python developers

## Example

This directory contains an example Starlark configuration for UnitAPI DSL:

- `example.star` - Speaker device configuration demonstrating Starlark syntax

## Structure

A typical Starlark configuration for UnitAPI includes:

1. **Version** - The version of the configuration format
2. **Extensions** - Definitions of device capabilities and requirements
3. **Devices** - Definitions of physical or virtual hardware
4. **Pipelines** - Workflows that connect devices and process data
5. **Functions** - Reusable code blocks for generating configurations

## Testing

You can test the Starlark configuration using the provided `test.py` script:

```bash
# Run the test script
python test.py

# Test with a different configuration file
python test.py --config other_config.star

# Validate without executing
python test.py --dry-run

# Convert to another format
python test.py --convert-to yaml

# List all pipelines in the configuration
python test.py --list-pipelines
```

## When to Use Starlark

Starlark is a good choice when:

- You need to generate configurations programmatically
- Your configuration requires complex logic or data manipulation
- You want to create reusable components or templates
- You prefer a Python-like syntax
- You need to perform calculations or transformations within the configuration

## Syntax Highlights

```python
# This is a comment

VERSION = "1.0"

# Define extensions
speaker_ext = extension(
    name = "speaker",
    version = ">=1.0.0",
    config = {
        "sample_rate": 48000,
        "channels": 2
    }
)

# Define devices
living_room_speaker = device(
    id = "living-room-speaker",
    type = "speaker",
    capabilities = ["playback", "streaming", "bluetooth"]
)

# Define pipelines
music_playback = pipeline(
    name = "music-playback",
    target = living_room_speaker.id,
    steps = [
        step("load", source="/music/playlist.m3u"),
        step("process", equalizer_preset="music"),
        step("play", volume=0.7, repeat=True)
    ]
)

# Function to create a multi-room audio pipeline
def create_multiroom_pipeline(name, sources, targets, volume=0.6):
    """Create a multi-room audio pipeline"""
    return pipeline(
        name = name,
        steps = [
            step("sync", devices=targets),
            step("load", source=sources),
            step("process", latency_compensation=True),
            step("play", volume=volume, synchronized=True)
        ]
    )

# Create a multi-room audio pipeline
whole_house_audio = create_multiroom_pipeline(
    name = "whole-house-audio",
    sources = ["/music/ambient.mp3", "/music/relaxing.mp3"],
    targets = [living_room_speaker.id, kitchen_speaker.id],
    volume = 0.5
)
```

## Learn More

For more information about UnitAPI DSL and its supported formats, see the main [DSL documentation](../../../docs/dsl.md).
