# UnitAPI Usage Guide

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
