
# UnitAPI: Universal Interface for Network Devices [<span style='font-size:20px;'>&#x270D;</span>](git@github.com:UnitApi/python/edit/main/docs/index.md)

## Overview

UnitAPI is a comprehensive Python framework for managing and interacting with network-connected devices across different platforms and protocols. It provides a unified, flexible, and secure approach to device communication and control.

## Key Features

### 1. Device Management
- Automatic device discovery
- Dynamic device registration
- Multi-protocol support
- Flexible device abstraction

### 2. Communication Protocols
- WebSocket
- MQTT
- Custom protocol extensions

### 3. Security
- Token-based authentication
- Encryption
- Access control
- Audit logging

### 4. Device Types
- Cameras
- Microphones
- Speakers
- GPIO Controllers
- Custom device implementations

## Architecture

```
+-------------------+
|   Device Layer   |
|  +--------------+|
|  | Device Types ||
|  +--------------+|
+-------------------+
         |
+-------------------+
| Protocol Layer   |
|  +--------------+|
|  | Protocols    ||
|  +--------------+|
+-------------------+
         |
+-------------------+
| Core Framework   |
|  +--------------+|
|  | Server       ||
|  | Client       ||
|  | Security     ||
|  +--------------+|
+-------------------+
```

## Quick Start

### Installation

```bash
pip install unitapi
```

#### Optional Protocol Support
```bash
# Install with specific protocol support
pip install unitapi[mqtt]
pip install unitapi[websocket]
```

### Basic Usage

#### Server Setup
```python
from unitapi.core.server import UnitAPIServer

# Create a server instance
server = UnitAPIServer(host='0.0.0.0', port=7890)

# Register a device
server.register_device(
    device_id='temp_sensor_01', 
    device_type='sensor',
    metadata={
        'location': 'living_room',
        'capabilities': ['temperature', 'humidity']
    }
)

# Start the server
server.start()
```

#### Client Interaction
```python
from unitapi.core.client import UnitAPIClient

# Create a client
client = UnitAPIClient(server_host='localhost', server_port=7890)

# List available devices
devices = client.list_devices()
print("Available Devices:", devices)
```

## Core Concepts

### 1. Devices
- Represent physical or virtual network-connected devices
- Provide a consistent interface for interaction
- Support custom device type creation

### 2. Protocols
- Abstraction layer for different communication methods
- Easy integration of new protocols
- Seamless device communication

### 3. Security
- Comprehensive authentication mechanisms
- Fine-grained access control
- Encryption of device communications

## Use Cases

- Smart Home Automation
- Industrial IoT
- Remote Monitoring
- Network Device Management
- Distributed Sensor Networks
- Remote Audio Control

## Documentation Sections

1. [Installation Guide](installation.md)
2. [Usage Guide](usage.md)
3. [Device Types](device_types.md)
4. [Protocols](protocols.md)
5. [Security](security.md)
6. [Examples](examples.md)
7. [Remote Speaker Agent](remote_speaker_agent.md)

## Contributing

We welcome contributions! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Support

- GitHub Issues: [UnitAPI Issues](https://github.com/UnitApi/python/issues)
- Email: support@unitapi.com

## License

UnitAPI is open-source software licensed under the MIT License.

## Version

Current Version: 0.1.5

## Compatibility

- Python 3.8+
- Supported Platforms:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Debian 10+)
  - Raspberry Pi (Raspbian/Raspberry Pi OS)

## Performance Characteristics

- Low-latency device communication
- Minimal overhead
- Scalable architecture
- Async-first design

## Roadmap

### Upcoming Features
- Enhanced machine learning integration
- More device type support
- Advanced discovery mechanisms
- Cloud service integrations
- Improved remote device management

## Disclaimer

UnitAPI is an evolving project. While we strive for stability, 
the API may change in future versions.

## Acknowledgments

Thanks to all contributors and the open-source community 
for making this project possible.

# UnitAPI Installation Guide [<span style='font-size:20px;'>&#x270D;</span>](git@github.com:UnitApi/python/edit/main/docs/installation.md)

## Prerequisites

- Python 3.8+
- pip package manager

## Installation Methods

### 1. pip Installation (Recommended)

```bash
pip install unitapi
```

### 2. Optional Protocol Support

```bash
# Install with MQTT support
pip install unitapi[mqtt]

# Install with WebSocket support
pip install unitapi[websocket]
```

### 3. From Source

```bash
# Clone the repository
git clone https://github.com/UnitApi/python.git
cd unitapi

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install .
```

## Verification

To verify the installation, run:

```bash
python -c "import unitapi; print(unitapi.__version__)"
```

## Dependencies

### Core Dependencies
- `asyncio`
- `pydantic`
- `cryptography`
- `python-jose`

### Optional Dependencies
- `paho-mqtt` (for MQTT support)
- `websockets` (for WebSocket support)
- `pyaudio` (for audio device support)
- `opencv-python` (for camera support)

## Troubleshooting

### Common Installation Issues

1. **Python Version Compatibility**
   - Ensure you're using Python 3.8 or newer
   - Use `python3 -m pip install unitapi` if multiple Python versions are installed

2. **Permission Issues**
   - On Unix-like systems, use `sudo pip install unitapi` 
   - Recommended: Use virtual environments

3. **Dependency Conflicts**
   - Create a virtual environment before installation
   ```bash
   python3 -m venv unitapi_env
   source unitapi_env/bin/activate  # On Windows: unitapi_env\Scripts\activate
   pip install unitapi
   ```

4. **PyAudio Installation Issues**
   - On Linux, you may need to install PortAudio development headers:
   ```bash
   sudo apt-get install portaudio19-dev
   pip install pyaudio
   ```
   - On macOS, you can use Homebrew:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```
   - On Windows, you might need to install a pre-built wheel:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

## Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/UnitApi/python.git
cd unitapi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Activate virtual environment

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .
```

## System-Specific Notes

### Raspberry Pi
- Ensure `python3-dev` package is installed
```bash
sudo apt-get update
sudo apt-get install python3-dev
pip install unitapi
```

### Docker
```dockerfile
FROM python:3.9-slim

# Install UnitAPI
RUN pip install unitapi

# Optional: Install additional protocol support
RUN pip install unitapi[mqtt,websocket]
```

## Updating UnitAPI

```bash
# Upgrade to latest version
pip install --upgrade unitapi

# Upgrade with specific protocol support
pip install --upgrade unitapi[mqtt]
```

## Uninstallation

```bash
pip uninstall unitapi
```

## Remote Speaker Agent Installation

For installing the Remote Speaker Agent on a remote machine, see the [Remote Speaker Agent documentation](remote_speaker_agent.md).

### Quick Remote Installation

```bash
# Install on a remote machine via SSH
scripts/install_remote_speaker_agent_via_ssh.sh remote-host [remote-user]

# Example:
scripts/install_remote_speaker_agent_via_ssh.sh 192.168.1.100 pi

# UnitAPI Usage Guide [<span style='font-size:20px;'>&#x270D;</span>](git@github.com:UnitApi/python/edit/main/docs/usage.md)

## Basic Concepts

UnitAPI provides a flexible framework for managing network-connected devices across different protocols and platforms.

## Core Components

- **Server**: Manages device registration and communication
- **Client**: Interacts with the server to control devices
- **Devices**: Represent different types of network peripherals
- **Protocols**: Support for various communication methods

## Quick Start

### Starting a Server

```python
from unitapi.core.server import UnitAPIServer

# Create a server instance
server = UnitAPIServer(host='localhost', port=7890)

# Register a device
server.register_device(
    device_id='temp_sensor_01', 
    device_type='sensor',
    metadata={
        'location': 'living_room',
        'capabilities': ['temperature', 'humidity']
    }
)

# Start the server
server.start()
```

### Client Interaction

```python
from unitapi.core.client import UnitAPIClient

# Create a client
client = UnitAPIClient(server_host='localhost', server_port=7890)

# List available devices
devices = client.list_devices()
print("Available Devices:", devices)

# List specific device type
sensor_devices = client.list_devices(device_type='sensor')
print("Sensor Devices:", sensor_devices)
```

## Device Types

### Camera Devices

```python
from unitapi.devices.camera import CameraDevice
import asyncio

# Create a camera device
camera = CameraDevice(
    device_id='camera_01',
    name='Main Camera',
    metadata={
        'resolution': '1080p',
        'fps': 30,
        'location': 'front_door'
    }
)

# Connect to the camera
await camera.connect()

# Capture an image
image_data = await camera.capture_image()
print(f"Image captured: {image_data}")

# Start a video stream
stream_info = await camera.start_video_stream(duration=10)
print(f"Stream started: {stream_info}")
```

### Microphone Devices

```python
from unitapi.devices.microphone import MicrophoneDevice
import asyncio

# Create a microphone device
mic = MicrophoneDevice(
    device_id='mic_01',
    name='Desktop Microphone',
    metadata={
        'sample_rate': 44100,
        'channels': 2,
        'location': 'office'
    }
)

# Connect to the microphone
await mic.connect()

# Record audio
audio_data = await mic.record_audio(duration=5, sample_rate=44100)
print(f"Audio recorded: {audio_data}")
```

### GPIO Devices

```python
from unitapi.devices.gpio import GPIODevice
import asyncio

# Create GPIO device
gpio = GPIODevice(
    device_id='rpi_gpio_01', 
    name='Raspberry Pi GPIO',
    metadata={'total_pins': 40}
)

# Connect to the GPIO device
await gpio.connect()

# Set pin mode and control
await gpio.set_pin_mode(18, 'output')
await gpio.digital_write(18, True)

# Read from a pin
await gpio.set_pin_mode(17, 'input')
pin_value = await gpio.digital_read(17)
print(f"Pin 17 value: {pin_value}")

# PWM control
await gpio.set_pin_mode(12, 'output')
await gpio.pwm_write(12, 0.5)  # 50% duty cycle
```

## Device Discovery

UnitAPI provides a comprehensive device discovery mechanism that can detect devices on the local network and on the local machine.

```python
from examples.device_discovery import DeviceDiscoveryService
import asyncio

# Create a discovery service
discovery = DeviceDiscoveryService(
    server_host='0.0.0.0',
    server_port=7890,
    discovery_port=7891,
    debug=True
)

# Discover devices
devices = await discovery.discover_devices()
print(f"Discovered {len(devices)} devices")

# Start the discovery service
await discovery.start()
```

## Remote Speaker Agent

UnitAPI includes a Remote Speaker Agent that allows you to control speakers on a remote machine. See the [Remote Speaker Agent documentation](remote_speaker_agent.md) for details.

```python
# Connect to a remote speaker agent
from unitapi.core.client import UnitAPIClient
import asyncio

# Create a client
client = UnitAPIClient(server_host='remote-host', server_port=7890)

# List available speakers
speakers = await client.list_devices(device_type='speaker')
print("Available Speakers:", speakers)

# Play audio on a specific speaker
await client.execute_command(
    device_id='speaker_01',
    command='play_audio',
    params={
        'file': 'path/to/audio.wav'
    }
)
```

## Authentication and Security

```python
from unitapi.security.authentication import AuthenticationManager

# Create authentication manager
auth_manager = AuthenticationManager()

# Register a user
await auth_manager.register_user(
    username='admin', 
    password='secure_password', 
    roles=['admin', 'user']
)

# Authenticate
token = await auth_manager.authenticate('admin', 'secure_password')
```

## Protocol Support

### WebSocket Protocol

```python
from unitapi.protocols.websocket import WebSocketProtocol
import asyncio

# Create WebSocket protocol handler
ws_client = WebSocketProtocol(host='localhost', port=8765)

# Connect and send message
await ws_client.connect()
await ws_client.send('device_command', {
    'device_id': 'sensor_01',
    'command': 'read_temperature'
})

# Add a message handler
async def handle_temperature_data(data):
    print(f"Received temperature: {data}")

ws_client.add_message_handler('temperature_data', handle_temperature_data)

# Disconnect when done
await ws_client.disconnect()
```

### MQTT Protocol

```python
from unitapi.protocols.mqtt import MQTTProtocol
import asyncio

# Create MQTT protocol handler
mqtt_client = MQTTProtocol(broker='localhost', port=1883)

# Connect and publish
await mqtt_client.connect()
await mqtt_client.publish('unitapi/devices/temperature', '22.5')

# Subscribe to a topic
await mqtt_client.subscribe('unitapi/devices/+/status')

# Add a message handler
def handle_status_message(topic, payload):
    print(f"Received status on {topic}: {payload}")

mqtt_client.add_message_handler('unitapi/devices/+/status', handle_status_message)
```

## Docker Support

UnitAPI includes Docker examples that demonstrate how to containerize UnitAPI applications. See the [Docker example README](../examples/docker/README.md) for details.

```bash
# Navigate to the docker example directory
cd examples/docker

# Start the containers
docker-compose up -d

# Access the client container
docker exec -it unitapi-speaker-client bash
```

## Error Handling

```python
try:
    # Device operations
    await device.connect()
    data = await device.read_sensor()
except Exception as e:
    # Handle connection or read errors
    print(f"Device error: {e}")
```

## Best Practices

1. Always use async/await for device operations
2. Implement proper error handling
3. Use authentication and access control
4. Keep sensitive information secure
5. Monitor device states and connections
6. Use device discovery for automatic setup

## Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Extensibility

You can easily extend UnitAPI by:
- Creating custom device types
- Implementing new protocol handlers
- Adding dynamic access rules
- Integrating with existing systems

# UnitAPI Remote Speaker Agent [<span style='font-size:20px;'>&#x270D;</span>](git@github.com:UnitApi/python/edit/main/docs/remote_speaker_agent.md)

The UnitAPI Remote Speaker Agent allows you to manage and control speakers on a remote PC via SSH. This document explains how to install, configure, and use this feature.

## Overview

The Remote Speaker Agent is a service that runs on a remote machine and provides access to all speakers on that machine through the UnitAPI protocol. This allows you to:

- Discover all speakers on the remote machine
- Play audio on specific speakers
- Test speakers with test tones
- Stream audio from one machine to speakers on another

## Installation

There are two ways to install the Remote Speaker Agent:

### 1. Direct Installation on the Remote Machine

If you have direct access to the remote machine, you can install the agent directly:

```bash
# Log in to the remote machine
ssh user@remote-host

# Clone the UnitAPI repository (if not already done)
git clone https://github.com/UnitApi/python.git
cd UnitApi/python

# Run the installation script
sudo scripts/install_remote_speaker_agent.sh
```

### 2. Remote Installation via SSH

If you only have SSH access to the remote machine, you can install the agent remotely from your local machine:

```bash
# Clone the UnitAPI repository (if not already done)
git clone https://github.com/UnitApi/python.git
cd UnitApi/python

# Run the remote installation script
scripts/install_remote_speaker_agent_via_ssh.sh remote-host [remote-user]

# Example:
scripts/install_remote_speaker_agent_via_ssh.sh 192.168.1.100 pi
```

The remote installation script will:
1. Connect to the remote machine via SSH
2. Copy the installation script to the remote machine
3. Execute the installation script on the remote machine
4. Create a local client script for testing the remote speakers

## Managing the Remote Speaker Agent

After installation, you can manage the Remote Speaker Agent on the remote machine using the following commands:

```bash
# List all available speakers
ssh user@remote-host 'sudo unitapi-speaker --list'

# Test all speakers
ssh user@remote-host 'sudo unitapi-speaker --test'

# Check the service status
ssh user@remote-host 'sudo unitapi-speaker --status'

# Start the service
ssh user@remote-host 'sudo unitapi-speaker --start'

# Stop the service
ssh user@remote-host 'sudo unitapi-speaker --stop'

# Enable the service to start at boot
ssh user@remote-host 'sudo unitapi-speaker --enable'

# Disable the service from starting at boot
ssh user@remote-host 'sudo unitapi-speaker --disable'
```

## Connecting to the Remote Speaker Agent

### Using the Python Client

To connect to the Remote Speaker Agent from another machine, you can use the UnitAPI client:

```python
from unitapi.core.client import UnitAPIClient
import asyncio

async def main():
    # Create a client
    client = UnitAPIClient(server_host='remote-host', server_port=7890)
    
    # List available speakers
    devices = await client.list_devices(device_type='speaker')
    print("Available Speakers:", devices)
    
    # Play audio on a specific speaker
    await client.execute_command(
        device_id='speaker_01',
        command='play_audio',
        params={
            'file': 'path/to/audio.wav'
        }
    )

# Run the async function
asyncio.run(main())
```

### Using the Command-Line Client

If you used the remote installation script, a client script was created for you:

```bash
# List all available speakers
python remote_speaker_client.py --host remote-host --list

# Test all speakers
python remote_speaker_client.py --host remote-host --test

# Test a specific speaker
python remote_speaker_client.py --host remote-host --device speaker_id

# Play an audio file on a specific speaker
python remote_speaker_client.py --host remote-host --device speaker_id --file path/to/audio.wav

# Play a test tone with custom frequency and duration
python remote_speaker_client.py --host remote-host --device speaker_id --frequency 880 --duration 2.0
```

## Docker Example

UnitAPI includes a Docker Compose example that demonstrates how to set up a virtual speaker server on one machine and a client on another machine using Docker. This example simulates the process of installing the UnitAPI speaker agent on a remote PC and controlling its speakers.

To use this example:

```bash
# Navigate to the docker example directory
cd examples/docker

# Start the containers
docker-compose up -d

# View the logs
docker-compose logs -f

# Access the client container and test the speakers
docker exec -it unitapi-speaker-client bash
python /opt/unitapi/client.py --host 172.28.1.2 --list
python /opt/unitapi/client.py --host 172.28.1.2 --test
```

For more details, see the [Docker example README](../examples/docker/README.md).

## Technical Details

The Remote Speaker Agent consists of the following components:

1. **UnitAPI Server**: Handles device registration and communication
2. **WebSocket Server**: Provides a WebSocket interface for real-time communication
3. **Speaker Detection**: Automatically detects all speakers on the system
4. **Speaker Registry**: Maintains a registry of all available speakers
5. **Configuration**: Stores speaker configuration in `/etc/unitapi/speaker_agent.json`
6. **Systemd Service**: Runs the agent as a system service (`unitapi-speaker-agent`)

The agent is installed in `/opt/unitapi` and runs in a Python virtual environment to avoid conflicts with system packages.

## Troubleshooting

If you encounter issues with the Remote Speaker Agent, check the following:

1. **Service Status**: Check if the service is running
   ```bash
   ssh user@remote-host 'sudo systemctl status unitapi-speaker-agent'
   ```

2. **Logs**: Check the service logs
   ```bash
   ssh user@remote-host 'sudo journalctl -u unitapi-speaker-agent'
   ```

3. **Configuration**: Check the configuration file
   ```bash
   ssh user@remote-host 'sudo cat /etc/unitapi/speaker_agent.json'
   ```

4. **Network**: Make sure the remote machine is reachable and the required ports are open
   ```bash
   # Test connectivity
   ping remote-host
   
   # Test if the UnitAPI port is open
   nc -zv remote-host 7890
   
   # Test if the WebSocket port is open
   nc -zv remote-host 8765
   ```

5. **Dependencies**: Make sure all required dependencies are installed
   ```bash
   ssh user@remote-host 'sudo /opt/unitapi/venv/bin/pip list | grep -E "pyaudio|websockets|numpy|sounddevice|soundfile"'
   ```

## Advanced Usage

### Custom Configuration

You can customize the Remote Speaker Agent by editing the configuration file:

```bash
ssh user@remote-host 'sudo nano /etc/unitapi/speaker_agent.json'
```

Configuration options:
- `auto_register_speakers`: Whether to automatically register all detected speakers (default: `true`)
- `speakers`: List of manually configured speakers (used when `auto_register_speakers` is `false`)

### Multiple Remote Machines

You can install the Remote Speaker Agent on multiple machines and control them all from a single client:

```bash
# Install on multiple machines
scripts/install_remote_speaker_agent_via_ssh.sh machine1 user1
scripts/install_remote_speaker_agent_via_ssh.sh machine2 user2

# Connect to each machine
python remote_speaker_client.py --host machine1 --list
python remote_speaker_client.py --host machine2 --list

# Play audio on specific speakers on different machines
python remote_speaker_client.py --host machine1 --device speaker_id1 --file audio1.wav
python remote_speaker_client.py --host machine2 --device speaker_id2 --file audio2.wav
```

### Integration with Other UnitAPI Devices

The Remote Speaker Agent can be integrated with other UnitAPI devices, such as microphones, cameras, and sensors, to create a complete IoT system:

```python
from unitapi.core.client import UnitAPIClient

# Connect to multiple UnitAPI servers
speaker_client = UnitAPIClient(server_host="speaker-host", server_port=7890)
microphone_client = UnitAPIClient(server_host="microphone-host", server_port=7890)
camera_client = UnitAPIClient(server_host="camera-host", server_port=7890)

# List devices on each server
speakers = await speaker_client.list_devices(device_type="speaker")
microphones = await microphone_client.list_devices(device_type="microphone")
cameras = await camera_client.list_devices(device_type="camera")

# Create a complete IoT system
# ...

---
+ Modular Documentation made possible by the [FlatEdit](http://www.flatedit.com) project.
