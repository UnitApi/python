
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
- gRPC
- Custom protocol extensions

### 3. Security
- Token-based authentication
- Encryption
- Access control
- Audit logging

### 4. Device Types
- Sensors
- Cameras
- Audio Devices
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
pip install unitapi[grpc]
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

## Documentation Sections

1. [Installation Guide](installation.md)
2. [Usage Guide](usage.md)
3. [Device Types](device_types.md)
4. [Protocols](protocols.md)
5. [Security](security.md)
6. [Examples](examples.md)

## Contributing

We welcome contributions! Please read our [Contribution Guidelines](CONTRIBUTING.md) for details on how to get started.

## Support

- GitHub Issues: [UnitAPI Issues](https://github.com/yourusername/unitapi/issues)
- Email: support@unitapi.com

## License

UnitAPI is open-source software licensed under the MIT License.

## Version

Current Version: 0.1.0

## Compatibility

- Python 3.8+
- Supported Platforms:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Debian 10+)

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

# Install with gRPC support
pip install unitapi[grpc]
```

### 3. From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/unitapi.git
cd unitapi

# Install dependencies
pip install -r requirements.txt

# Install thepackage
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
- `grpcio` (for gRPC support)

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

## Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/yourusername/unitapi.git
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

### Sensor Devices

```python
from unitapi.devices.base import SensorDevice

class TemperatureSensor(SensorDevice):
    async def read_sensor(self, sensor_type='temperature'):
        # Custom sensor reading logic
        return {
            'temperature': 22.5,
            'unit': '°C'
        }
```

### GPIO Devices

```python
from unitapi.devices.gpio import GPIODevice

# Create GPIO device
gpio = GPIODevice(
    device_id='rpi_gpio_01', 
    name='Raspberry Pi GPIO',
    metadata={'total_pins': 40}
)

# Set pin mode and control
await gpio.set_pin_mode(18, 'output')
await gpio.digital_write(18, True)
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

### MQTT Protocol

```python
from unitapi.protocols.mqtt import MQTTProtocol

# Create MQTT protocol handler
mqtt_client = MQTTProtocol(broker='localhost', port=1883)

# Connect and publish
await mqtt_client.connect()
await mqtt_client.publish('unitapi/devices/temperature', '22.5')
```

### WebSocket Protocol

```python
from unitapi.protocols.websocket import WebSocketProtocol

# Create WebSocket protocol handler
ws_client = WebSocketProtocol(host='localhost', port=8765)

# Connect and send message
await ws_client.connect()
await ws_client.send('device_command', {
    'device_id': 'sensor_01',
    'command': 'read_temperature'
})
```

## Access Control

```python
from unitapi.security.access_control import AccessControlManager

# Create access control manager
acl_manager = AccessControlManager()

# Define a dynamic access rule
def temperature_limit_rule(role, resource, action, context):
    if resource == 'temperature_sensor' and action == 'write':
        # Prevent temperature changes beyond safe limits
        temp = context.get('temperature', 0)
        return 18 <= temp <= 30
    return True

# Add dynamic rule
acl_manager.add_dynamic_rule(temperature_limit_rule)

# Check access
is_allowed = acl_manager.check_access(
    role='operator', 
    resource='temperature_sensor', 
    action='write',
    context={'temperature': 22}
)
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

---
+ Modular Documentation made possible by the [FlatEdit](http://www.flatedit.com) project.
