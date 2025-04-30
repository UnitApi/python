# PC Examples for UnitAPI

This directory contains examples for using UnitAPI with various devices on a PC. These examples demonstrate how to control and interact with different hardware devices, both locally and remotely.

## Directory Structure

- `camera/`: Examples for controlling webcams and capturing images/videos
- `keyboard/`: Examples for controlling keyboards and sending keystrokes
- `microphone/`: Examples for recording audio and processing microphone input
- `mouse/`: Examples for controlling mouse movements and clicks
- `speaker/`: Examples for playing audio and controlling speakers
- `misc/`: Miscellaneous examples that don't fit into the other categories

## Device Types

Each subdirectory contains examples for a specific device type:

### Camera Examples

The `camera/` directory contains examples for working with webcams and other camera devices. These examples demonstrate how to capture images, record videos, and process camera frames.

### Keyboard Examples

The `keyboard/` directory contains examples for working with keyboards. These examples demonstrate how to send keystrokes, handle keyboard events, and control keyboards remotely.

### Microphone Examples

The `microphone/` directory contains examples for working with microphones. These examples demonstrate how to record audio, process microphone input, and measure audio levels.

### Mouse Examples

The `mouse/` directory contains examples for working with mice. These examples demonstrate how to control mouse movements, handle mouse clicks, and automate mouse actions.

### Speaker Examples

The `speaker/` directory contains examples for working with speakers. These examples demonstrate how to play audio files, generate sounds, and control audio playback.

## Client-Server Architecture

Many examples follow a client-server architecture:

- **Server**: Runs on the device you want to control and exposes its functionality through UnitAPI
- **Client**: Connects to the server and controls the device remotely

This architecture allows you to:

1. Control devices on remote machines
2. Create distributed applications
3. Implement device sharing and remote access
4. Build automation systems that span multiple devices

## Running the Examples

Each subdirectory contains its own README.md file with specific instructions for running the examples. In general, you can run the examples using Python:

```bash
# Run a client example
python examples/pc/device_type/example_client.py

# Run a server example
python examples/pc/device_type/example_server.py --host 0.0.0.0 --port 7890
```

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- Device-specific dependencies (see individual README files)

## Common Options

Most server examples support the following command-line options:

- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging

Most client examples support:

- `--host`: Server host to connect to (default: localhost)
- `--port`: Server port to connect to (default: 7890)
- `--debug`: Enable debug logging

## Security Considerations

When running servers that expose device functionality, consider the following security practices:

1. Run servers on secure, private networks
2. Use UnitAPI's authentication and encryption features
3. Implement appropriate access controls
4. Be cautious about exposing sensitive devices to remote access

## Additional Resources

For more information about UnitAPI and its capabilities, see the documentation in the `docs/` directory.
