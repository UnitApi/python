# UnitAPI: Universal Hardware Interface as Network Devices

## Overview

UnitAPI (Unit Hardware API) is a comprehensive Python framework for managing and interacting with network-connected hardware devices across different platforms and protocols. It provides a unified, flexible, and secure approach to device communication and control.

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

### High-Level Architecture

```mermaid
graph TD
    A[Device Layer] --> B[Protocol Layer]
    B --> C[Core Framework]
    
    subgraph "Device Layer"
        A1[Device Types]
    end
    
    subgraph "Protocol Layer"
        B1[Protocols]
    end
    
    subgraph "Core Framework"
        C1[Server]
        C2[Client]
        C3[Security]
    end
```

### Component Diagram

```mermaid
graph TD
    Client[Client API] --> |Requests| Server[Server API]
    Server --> |Manages| Devices[Device Registry]
    Server --> |Uses| Security[Security Module]
    Server --> |Communicates via| Protocols[Protocol Handlers]
    Protocols --> |Connect to| Devices
    
    subgraph "Device Types"
        D1[Camera]
        D2[Microphone]
        D3[Speaker]
        D4[GPIO]
        D5[Input Devices]
    end
    
    Devices --> D1
    Devices --> D2
    Devices --> D3
    Devices --> D4
    Devices --> D5
```

### Device Inheritance Structure

```mermaid
classDiagram
    BaseDevice <|-- Camera
    BaseDevice <|-- Microphone
    BaseDevice <|-- Speaker
    BaseDevice <|-- GPIO
    BaseDevice <|-- InputDevice
    InputDevice <|-- Keyboard
    InputDevice <|-- Mouse
    InputDevice <|-- Touchscreen
    InputDevice <|-- Gamepad
    
    class BaseDevice {
        +device_id: str
        +device_type: str
        +metadata: dict
        +connect()
        +disconnect()
        +is_connected(): bool
    }
    
    class Camera {
        +capture_frame()
        +start_stream()
        +stop_stream()
    }
    
    class Microphone {
        +record_audio()
        +start_recording()
        +stop_recording()
    }
    
    class Speaker {
        +play_audio()
        +set_volume()
        +get_volume()
    }
```

### Communication Sequence

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Device
    
    Client->>Server: Connect()
    Server-->>Client: Connection Established
    
    Client->>Server: List Devices()
    Server-->>Client: Available Devices
    
    Client->>Server: Connect to Device(device_id)
    Server->>Device: Establish Connection
    Device-->>Server: Connection Status
    Server-->>Client: Device Connected
    
    Client->>Server: Send Command(device_id, command, params)
    Server->>Device: Execute Command
    Device-->>Server: Command Result
    Server-->>Client: Command Response
    
    Client->>Server: Disconnect from Device(device_id)
    Server->>Device: Close Connection
    Device-->>Server: Disconnected
    Server-->>Client: Device Disconnected
    
    Client->>Server: Disconnect()
    Server-->>Client: Connection Closed
```

### Device Discovery Process

```mermaid
flowchart TD
    A[Start Discovery] --> B{Local Network Scan}
    B --> C[Find Devices]
    C --> D{For Each Device}
    D --> E[Query Device Info]
    E --> F{Supported Protocol?}
    F -->|Yes| G[Register Device]
    F -->|No| H[Skip Device]
    G --> I[Next Device]
    H --> I
    I --> J{More Devices?}
    J -->|Yes| D
    J -->|No| K[Discovery Complete]
```

### Device Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: connect()
    Connecting --> Connected: connection_established
    Connecting --> Error: connection_failed
    Connected --> Active: device_ready
    Active --> Idle: no_activity
    Idle --> Active: new_command
    Active --> Error: command_failed
    Error --> Reconnecting: auto_reconnect
    Reconnecting --> Connected: reconnection_successful
    Reconnecting --> Disconnected: reconnection_failed
    Connected --> Disconnecting: disconnect()
    Active --> Disconnecting: disconnect()
    Idle --> Disconnecting: disconnect()
    Disconnecting --> Disconnected: disconnection_complete
    Disconnected --> [*]
```

### Deployment Architecture

```mermaid
graph TD
    subgraph "Cloud Environment"
        CloudServer[Central Management Server]
        Database[(Device Registry DB)]
        CloudServer --- Database
    end
    
    subgraph "Local Network A"
        GatewayA[Local Gateway]
        DeviceA1[Camera]
        DeviceA2[Microphone]
        DeviceA3[Speaker]
        GatewayA --- DeviceA1
        GatewayA --- DeviceA2
        GatewayA --- DeviceA3
    end
    
    subgraph "Local Network B"
        GatewayB[Local Gateway]
        DeviceB1[GPIO Controller]
        DeviceB2[Input Devices]
        GatewayB --- DeviceB1
        GatewayB --- DeviceB2
    end
    
    subgraph "Remote Devices"
        RemoteDevice1[Remote Camera]
        RemoteDevice2[Remote Speaker]
    end
    
    CloudServer --- GatewayA
    CloudServer --- GatewayB
    CloudServer --- RemoteDevice1
    CloudServer --- RemoteDevice2
    
    Client1[Client Application] --- CloudServer
    Client2[Client Application] --- GatewayA
    Client3[Client Application] --- GatewayB
```

### Network Topology

```mermaid
graph TD
    subgraph "Internet"
        Cloud[Cloud Services]
    end
    
    subgraph "Home Network"
        Router[Home Router]
        Server[UnitAPI Server]
        Dev1[Camera]
        Dev2[Microphone]
        Dev3[Speaker]
        
        Router --- Server
        Server --- Dev1
        Server --- Dev2
        Server --- Dev3
    end
    
    subgraph "Remote Location"
        RemoteRouter[Remote Router]
        RemoteDev1[Remote Camera]
        RemoteDev2[Remote Microphone]
        
        RemoteRouter --- RemoteDev1
        RemoteRouter --- RemoteDev2
    end
    
    Cloud --- Router
    Cloud --- RemoteRouter
    
    Client[Client Application] --- Cloud
    LocalClient[Local Client] --- Server
```

### Implementation Timeline

```mermaid
gantt
    title UnitAPI Implementation Timeline
    dateFormat  YYYY-MM-DD
    
    section Planning
    Requirements Analysis      :a1, 2024-01-01, 14d
    Architecture Design        :a2, after a1, 21d
    
    section Development
    Core Framework            :d1, after a2, 30d
    Protocol Implementation   :d2, after d1, 21d
    Device Types              :d3, after d1, 28d
    Security Features         :d4, after d2, 14d
    
    section Testing
    Unit Testing              :t1, after d3, 14d
    Integration Testing       :t2, after t1, 14d
    Performance Testing       :t3, after t2, 7d
    
    section Deployment
    Documentation             :p1, after d4, 14d
    Example Creation          :p2, after p1, 7d
    Release                   :milestone, after t3, 0d
```

### Device Type Distribution

```mermaid
pie title Device Types in Typical Deployment
    "Cameras" : 25
    "Microphones" : 20
    "Speakers" : 20
    "Input Devices" : 15
    "GPIO Controllers" : 10
    "Custom Devices" : 10
```

### User Experience Journey

```mermaid
journey
    title UnitAPI User Experience
    section Discovery
      Find UnitAPI: 5: User
      Read Documentation: 3: User
      Evaluate Features: 4: User
    section Installation
      Install Package: 5: User, Developer
      Configure Environment: 3: Developer
      Test Installation: 4: Developer
    section Development
      Create Server: 5: Developer
      Register Devices: 4: Developer
      Implement Client: 3: Developer
    section Deployment
      Test in Production: 2: Developer, Admin
      Monitor Performance: 3: Admin
      Scale System: 4: Admin
    section Maintenance
      Update Framework: 3: Developer, Admin
      Add New Devices: 5: Developer
      Troubleshoot Issues: 2: Developer, Admin
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
