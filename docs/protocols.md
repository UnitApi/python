# UnitAPI Protocols

UnitAPI supports multiple communication protocols for device interaction. This document provides detailed information about the built-in protocols and how to implement custom protocols.

## Overview

The protocol layer in UnitAPI provides an abstraction for different communication methods, allowing devices to communicate regardless of the underlying protocol. This enables seamless integration of devices that use different communication standards.

## Built-in Protocols

### 1. WebSocket Protocol

The WebSocket protocol provides real-time, bidirectional communication between clients and servers. It's ideal for applications that require low-latency, high-frequency updates.

#### Features
- Real-time bidirectional communication
- Message-based data exchange
- Support for both client and server roles
- Custom message handlers

#### Example Usage (Client)
```python
from unitapi.protocols.websocket import WebSocketProtocol
import asyncio

async def main():
    # Create WebSocket protocol handler
    ws_client = WebSocketProtocol(host='localhost', port=8765)
    
    # Connect to WebSocket server
    await ws_client.connect()
    
    # Define a message handler
    async def handle_temperature_data(data):
        print(f"Received temperature: {data}")
    
    # Register the message handler
    ws_client.add_message_handler('temperature_data', handle_temperature_data)
    
    # Send a message
    await ws_client.send('device_command', {
        'device_id': 'sensor_01',
        'command': 'read_temperature'
    })
    
    # Wait for some time to receive messages
    await asyncio.sleep(10)
    
    # Disconnect when done
    await ws_client.disconnect()

asyncio.run(main())
```

#### Example Usage (Server)
```python
from unitapi.protocols.websocket import WebSocketProtocol
import asyncio

async def main():
    # Create WebSocket protocol handler
    ws_server = WebSocketProtocol(host='0.0.0.0', port=8765)
    
    # Start WebSocket server
    await ws_server.create_server()
    
    # The server will handle incoming connections and messages automatically
    # based on the internal _handle_client and _process_message methods

asyncio.run(main())
```

### 2. MQTT Protocol

MQTT (Message Queuing Telemetry Transport) is a lightweight publish-subscribe messaging protocol designed for constrained devices and low-bandwidth, high-latency networks. It's ideal for IoT applications.

#### Features
- Publish-subscribe messaging pattern
- Quality of Service (QoS) levels
- Retained messages
- Last Will and Testament (LWT)

#### Example Usage
```python
from unitapi.protocols.mqtt import MQTTProtocol
import asyncio

async def main():
    # Create MQTT protocol handler
    mqtt_client = MQTTProtocol(broker='localhost', port=1883)
    
    # Connect to MQTT broker
    await mqtt_client.connect()
    
    # Define a message handler
    def handle_temperature_data(topic, payload):
        print(f"Received temperature on {topic}: {payload}")
    
    # Subscribe to a topic
    await mqtt_client.subscribe('unitapi/devices/+/temperature')
    
    # Register the message handler
    mqtt_client.add_message_handler('unitapi/devices/+/temperature', handle_temperature_data)
    
    # Publish a message
    await mqtt_client.publish('unitapi/devices/sensor_01/temperature', '22.5')
    
    # Wait for some time to receive messages
    await asyncio.sleep(10)
    
    # Disconnect when done
    await mqtt_client.disconnect()

asyncio.run(main())
```

## Protocol Selection

UnitAPI allows you to choose the appropriate protocol based on your application's requirements:

```python
from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.protocols.mqtt import MQTTProtocol
import asyncio

async def main():
    # Create a server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create protocol handlers
    websocket = WebSocketProtocol(host='0.0.0.0', port=8765)
    mqtt = MQTTProtocol(broker='localhost', port=1883)
    
    # Start the server and protocols
    server_task = asyncio.create_task(server.start())
    websocket_task = asyncio.create_task(websocket.create_server())
    
    # Connect MQTT client
    await mqtt.connect()
    
    # Wait for all tasks
    await asyncio.gather(server_task, websocket_task)

asyncio.run(main())
```

## Creating Custom Protocols

You can create custom protocols by implementing the necessary methods for your specific communication needs.

### Basic Custom Protocol

```python
import asyncio
import logging
from typing import Dict, Any, Callable

class CustomProtocol:
    """Custom protocol implementation."""
    
    def __init__(self, host: str, port: int):
        """Initialize custom protocol."""
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self._message_handlers = {}
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to the custom protocol server."""
        try:
            # Implement custom connection logic
            await asyncio.sleep(1)  # Simulate connection delay
            self._connected = True
            self.logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the custom protocol server."""
        try:
            # Implement custom disconnection logic
            await asyncio.sleep(0.5)  # Simulate disconnection delay
            self._connected = False
            self.logger.info(f"Disconnected from {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Disconnection failed: {e}")
            return False
    
    async def send(self, message_type: str, data: Dict[str, Any]) -> bool:
        """Send a message via the custom protocol."""
        try:
            if not self._connected:
                raise ConnectionError("Not connected")
            
            # Implement custom message sending logic
            self.logger.info(f"Sending message: {message_type}")
            
            # Simulate message sending
            await asyncio.sleep(0.2)
            
            return True
        except Exception as e:
            self.logger.error(f"Message sending failed: {e}")
            return False
    
    def add_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for specific message types."""
        self._message_handlers[message_type] = handler
        self.logger.info(f"Registered handler for message type: {message_type}")
    
    async def create_server(self) -> None:
        """Create a server for the custom protocol."""
        try:
            # Implement custom server creation logic
            self.logger.info(f"Starting server on {self.host}:{self.port}")
            
            # Simulate server running
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Server creation failed: {e}")
```

## Protocol Interoperability

UnitAPI's protocol abstraction allows devices to communicate regardless of the underlying protocol. This is achieved through a common message format and protocol-specific adapters.

### Example: Cross-Protocol Communication

```python
from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.protocols.mqtt import MQTTProtocol
import asyncio

async def main():
    # Create a server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create protocol handlers
    websocket = WebSocketProtocol(host='0.0.0.0', port=8765)
    mqtt = MQTTProtocol(broker='localhost', port=1883)
    
    # Connect protocols
    await websocket.connect()
    await mqtt.connect()
    
    # Define a message handler that bridges protocols
    async def bridge_temperature_data(data):
        # When temperature data is received via WebSocket,
        # republish it via MQTT
        if 'temperature' in data:
            device_id = data.get('device_id', 'unknown')
            temperature = data.get('temperature')
            await mqtt.publish(f'unitapi/devices/{device_id}/temperature', str(temperature))
    
    # Register the bridge handler
    websocket.add_message_handler('temperature_data', bridge_temperature_data)
    
    # Start the server
    await server.start()

asyncio.run(main())
```

## Best Practices

1. **Protocol Selection**: Choose the appropriate protocol based on your application's requirements:
   - WebSocket for real-time, bidirectional communication
   - MQTT for lightweight, publish-subscribe messaging in IoT applications

2. **Error Handling**: Implement proper error handling for connection, disconnection, and message sending/receiving.

3. **Message Handlers**: Use message handlers to process incoming messages asynchronously.

4. **Connection Management**: Ensure proper connection and disconnection to avoid resource leaks.

5. **Security**: Consider security implications when selecting and implementing protocols:
   - Use secure variants (WSS for WebSocket, MQTTS for MQTT)
   - Implement authentication and authorization
   - Encrypt sensitive data

6. **Logging**: Use the logging module to provide informative logs for debugging.

7. **Asynchronous Operations**: Always use `async`/`await` for protocol operations to ensure non-blocking behavior.
