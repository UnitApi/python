# UnitAPI Examples

UnitAPI includes a variety of example applications that demonstrate how to use the framework for different use cases. This document provides an overview of these examples and explains how to run them.

## Overview

The examples are located in the `examples/` directory and cover various aspects of UnitAPI, including:

- Device discovery and management
- Camera and microphone usage
- Speaker control
- Remote device control
- Docker containerization

## Basic Examples

### Device Discovery

The device discovery example demonstrates how to automatically discover and register devices on the local network.

**File**: `examples/device_discovery.py`

**Features**:
- Automatic discovery of local devices (cameras, microphones, speakers)
- Network scanning for UnitAPI-compatible devices
- mDNS (Bonjour/Zeroconf) discovery
- UDP broadcast discovery

**Running the Example**:
```bash
python examples/device_discovery.py --debug
```

**Additional Options**:
```bash
# Specify host and port
python examples/device_discovery.py --host 0.0.0.0 --port 7890

# Specify network range for scanning
python examples/device_discovery.py --network-range 192.168.1.0/24
```

### Camera Capture

The camera capture example demonstrates how to capture images from a camera device.

**File**: `examples/camera_capture.py`

**Features**:
- Camera device initialization
- Image capture
- Image saving

**Running the Example**:
```bash
python examples/camera_capture.py
```

### Camera Frame Capture

The camera frame capture example demonstrates how to capture individual frames from a camera device.

**File**: `examples/camera_frame_capture.py`

**Features**:
- Camera device initialization
- Continuous frame capture
- Frame processing

**Running the Example**:
```bash
python examples/camera_frame_capture.py
```

### Microphone Recording

The microphone recording example demonstrates how to record audio from a microphone device.

**File**: `examples/microphone_recording.py`

**Features**:
- Microphone device initialization
- Audio recording
- Audio saving

**Running the Example**:
```bash
python examples/microphone_recording.py
```

### Microphone Audio Input

The microphone audio input example demonstrates how to process real-time audio input from a microphone device.

**File**: `examples/microphone_audio_input.py`

**Features**:
- Microphone device initialization
- Real-time audio processing
- Audio visualization

**Running the Example**:
```bash
python examples/microphone_audio_input.py
```

### Speaker Playback

The speaker playback example demonstrates how to play audio on a speaker device.

**File**: `examples/speaker_playback.py`

**Features**:
- Speaker device initialization
- Audio file playback
- Test tone generation

**Running the Example**:
```bash
python examples/speaker_playback.py
```

### Speaker Audio Playback

The speaker audio playback example demonstrates how to play audio streams on a speaker device.

**File**: `examples/speaker_audio_playback.py`

**Features**:
- Speaker device initialization
- Audio stream playback
- Volume control

**Running the Example**:
```bash
python examples/speaker_audio_playback.py
```

### Take Screenshot

The take screenshot example demonstrates how to capture screenshots using UnitAPI.

**File**: `examples/take_screenshot.py`

**Features**:
- Screen capture
- Image saving
- Multi-monitor support

**Running the Example**:
```bash
python examples/take_screenshot.py
```

### Input Devices

The input devices example demonstrates how to use various input devices (mouse, keyboard, touchscreen, gamepad) with UnitAPI.

**File**: `examples/input_devices.py`

**Features**:
- Mouse control (movement, clicks, scrolling, dragging)
- Keyboard input (key presses, text typing, hotkeys)
- Touchscreen gestures (taps, swipes, pinches, rotations)
- Gamepad control (buttons, triggers, analog sticks, vibration)
- Command execution interface

**Running the Example**:
```bash
python examples/input_devices.py
```

## Remote Device Examples

### Remote Camera Capture

The remote camera capture example demonstrates how to capture images from a remote camera device.

**File**: `examples/remote_camera_capture.py`

**Features**:
- Remote camera device connection
- Image capture over the network
- Image saving

**Running the Example**:
```bash
python examples/remote_camera_capture.py --host remote-host
```

### Remote Camera Frame Capture

The remote camera frame capture example demonstrates how to capture frames from a remote camera device.

**File**: `examples/remote_camera_frame_capture.py`

**Features**:
- Remote camera device connection
- Continuous frame capture over the network
- Frame processing

**Running the Example**:
```bash
python examples/remote_camera_frame_capture.py --host remote-host
```

### Speaker Client

The speaker client example demonstrates how to control a remote speaker device.

**File**: `examples/speaker_client.py`

**Features**:
- Remote speaker device connection
- Audio playback control
- Speaker discovery

**Running the Example**:
```bash
python examples/speaker_client.py --host remote-host --list
python examples/speaker_client.py --host remote-host --test
python examples/speaker_client.py --host remote-host --device speaker_id --file audio.wav
```

### Remote Control

The remote control example demonstrates how to control various remote devices.

**File**: `examples/remote_control.py`

**Features**:
- Remote device discovery
- Unified device control interface
- Command execution

**Running the Example**:
```bash
python examples/remote_control.py --host remote-host
```

## Advanced Examples

### Stream Processing

The stream processing example demonstrates how to process data streams from devices.

**File**: `examples/stream_processing.py`

**Features**:
- Real-time data stream processing
- Stream transformation
- Stream visualization

**Running the Example**:
```bash
python examples/stream_processing.py
```

### Docker Examples

UnitAPI includes Docker examples that demonstrate how to containerize UnitAPI applications.

**Directory**: `examples/docker/`

#### Speaker Server and Client

The Docker example includes a speaker server and client setup that demonstrates how to use UnitAPI in a containerized environment.

**Files**:
- `examples/docker/docker-compose.yml`
- `examples/docker/speaker-server/Dockerfile`
- `examples/docker/speaker-server/entrypoint.sh`
- `examples/docker/speaker-server/virtual_speaker.py`
- `examples/docker/speaker-client/Dockerfile`
- `examples/docker/speaker-client/entrypoint.sh`
- `examples/docker/speaker-client/client.py`

**Features**:
- Containerized UnitAPI server and client
- Virtual speaker implementation
- Remote speaker agent installation via SSH
- Network configuration

**Running the Example**:
```bash
# Navigate to the docker example directory
cd examples/docker

# Start the containers
docker-compose up -d

# View the logs
docker-compose logs -f

# Access the client container
docker exec -it unitapi-speaker-client bash

# Inside the container, use the client script
python /opt/unitapi/client.py --host 172.28.1.2 --list
python /opt/unitapi/client.py --host 172.28.1.2 --test
```

## Creating Your Own Examples

You can use the provided examples as a starting point for creating your own UnitAPI applications. Here's a basic template:

```python
import asyncio
import logging
from unitapi.core.client import UnitAPIClient
from unitapi.core.server import UnitAPIServer
from unitapi.devices.base import BaseDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Create a server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Register a device
    server.register_device(
        device_id='my_device_01',
        device_type='custom',
        metadata={'capability': 'example'}
    )
    
    # Start the server in a separate task
    server_task = asyncio.create_task(server.start())
    
    # Create a client
    client = UnitAPIClient(server_host='localhost', server_port=7890)
    
    # List devices
    devices = await client.list_devices()
    print(f"Available devices: {devices}")
    
    # Execute a command on a device
    result = client.execute_command(
        device_id='my_device_01',
        command='status'
    )
    print(f"Command result: {result}")
    
    # Wait for the server task
    await server_task

if __name__ == "__main__":
    asyncio.run(main())
```

## Running All Examples

UnitAPI includes a script to run all examples sequentially:

```bash
python run_examples.py
```

You can also run specific examples:

```bash
python run_examples.py --example camera_capture
python run_examples.py --example microphone_recording
```

## Troubleshooting

If you encounter issues running the examples, check the following:

1. **Dependencies**: Make sure all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Device Permissions**: Some examples require access to hardware devices (cameras, microphones, speakers). Make sure your user has the necessary permissions.

3. **Network Configuration**: For remote device examples, make sure the remote host is reachable and the required ports are open.

4. **Docker Setup**: For Docker examples, make sure Docker and Docker Compose are installed and running.

## Conclusion

The examples provided with UnitAPI demonstrate various aspects of the framework and can serve as a starting point for your own applications. By exploring these examples, you can learn how to use UnitAPI effectively for your specific use case.
