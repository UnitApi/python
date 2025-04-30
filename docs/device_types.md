# UnitAPI Device Types

UnitAPI supports various device types, each with its own capabilities and interfaces. This document provides detailed information about the built-in device types and how to create custom device types.

## Overview

UnitAPI's device abstraction layer provides a consistent interface for interacting with different types of hardware and virtual devices. Each device type inherits from the `BaseDevice` class and implements specific functionality relevant to that device category.

## Built-in Device Types

### 1. Camera Devices

Camera devices provide interfaces for capturing images and video streams.

#### Features
- Image capture
- Video streaming
- Camera configuration (resolution, FPS)
- Connection management

#### Example Usage
```python
from unitapi.devices.camera import CameraDevice
import asyncio

async def main():
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
    
    # Disconnect when done
    await camera.disconnect()

asyncio.run(main())
```

### 2. Microphone Devices

Microphone devices provide interfaces for recording audio.

#### Features
- Audio recording
- Sample rate and channel configuration
- Connection management

#### Example Usage
```python
from unitapi.devices.microphone import MicrophoneDevice
import asyncio

async def main():
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
    
    # Disconnect when done
    await mic.disconnect()

asyncio.run(main())
```

### 3. GPIO Devices

GPIO (General Purpose Input/Output) devices provide interfaces for controlling digital pins, typically on devices like Raspberry Pi.

#### Features
- Pin mode configuration (input/output)
- Digital read/write operations
- PWM (Pulse Width Modulation) control
- Connection management

#### Example Usage
```python
from unitapi.devices.gpio import GPIODevice
import asyncio

async def main():
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
    
    # Disconnect when done
    await gpio.disconnect()

asyncio.run(main())
```

### 4. Speaker Devices

Speaker devices provide interfaces for playing audio.

#### Features
- Audio playback
- Volume control
- Audio format configuration
- Connection management

#### Example Usage
```python
from unitapi.devices.remote_speaker_device import RemoteSpeakerDevice
import asyncio

async def main():
    # Create a speaker device
    speaker = RemoteSpeakerDevice(
        device_id='speaker_01',
        name='Living Room Speaker',
        metadata={
            'sample_rate': 44100,
            'channels': 2,
            'location': 'living_room'
        }
    )
    
    # Connect to the speaker
    await speaker.connect()
    
    # Play audio
    await speaker.play_audio('path/to/audio.wav')
    
    # Play a test tone
    await speaker.play_test_tone(frequency=440, duration=2.0)
    
    # Disconnect when done
    await speaker.disconnect()

asyncio.run(main())
```

## Creating Custom Device Types

You can create custom device types by inheriting from the `BaseDevice` class or one of its subclasses.

### Basic Custom Device

```python
from unitapi.devices.base import BaseDevice, DeviceStatus
import asyncio
import logging

class CustomDevice(BaseDevice):
    """Custom device implementation."""
    
    def __init__(self, device_id: str, name: str, metadata=None):
        """Initialize custom device."""
        super().__init__(
            device_id=device_id,
            name=name,
            device_type="custom",
            metadata=metadata or {}
        )
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Connect to the device."""
        try:
            # Custom connection logic
            await asyncio.sleep(1)  # Simulate connection delay
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Device {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the device."""
        try:
            # Custom disconnection logic
            await asyncio.sleep(0.5)  # Simulate disconnection delay
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Device {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Disconnection failed: {e}")
            return False
    
    async def execute_command(self, command: str, params=None) -> dict:
        """Execute a command on the device."""
        try:
            if command == "custom_command":
                # Implement custom command logic
                return {"status": "success", "result": "Custom command executed"}
            else:
                raise ValueError(f"Unsupported command: {command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
```

### Custom Sensor Device

```python
from unitapi.devices.base import SensorDevice
import asyncio
import random
import logging

class TemperatureSensor(SensorDevice):
    """Temperature sensor implementation."""
    
    def __init__(self, device_id: str, name: str, metadata=None):
        """Initialize temperature sensor."""
        super().__init__(
            device_id=device_id,
            name=name,
            device_type="temperature_sensor",
            metadata=metadata or {}
        )
        self.logger = logging.getLogger(__name__)
        self.min_temp = metadata.get("min_temp", 15.0) if metadata else 15.0
        self.max_temp = metadata.get("max_temp", 30.0) if metadata else 30.0
    
    async def read_sensor(self) -> dict:
        """Read temperature data."""
        try:
            # Simulate temperature reading
            await asyncio.sleep(0.5)
            temperature = random.uniform(self.min_temp, self.max_temp)
            
            return {
                "device_id": self.device_id,
                "timestamp": asyncio.get_event_loop().time(),
                "temperature": round(temperature, 1),
                "unit": "°C"
            }
        except Exception as e:
            self.logger.error(f"Sensor reading failed: {e}")
            return {"error": str(e)}
```

## Device Registration

Once you've created a device, you need to register it with the UnitAPI server:

```python
from unitapi.core.server import UnitAPIServer
import asyncio

async def main():
    # Create a server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create a custom device
    custom_device = CustomDevice(
        device_id='custom_01',
        name='My Custom Device',
        metadata={'capability': 'custom_function'}
    )
    
    # Register the device
    server.register_device(
        device_id=custom_device.device_id,
        device_type=custom_device.type,
        metadata=custom_device.metadata
    )
    
    # Start the server
    await server.start()

asyncio.run(main())
```

## Device Discovery

UnitAPI provides a device discovery mechanism that can automatically detect and register devices:

```python
from examples.device_discovery import DeviceDiscoveryService
import asyncio

async def main():
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

asyncio.run(main())
```

## Best Practices

1. **Asynchronous Operations**: Always use `async`/`await` for device operations to ensure non-blocking behavior.
2. **Error Handling**: Implement proper error handling in all device methods.
3. **Logging**: Use the logging module to provide informative logs for debugging.
4. **Status Management**: Keep the device status updated (`ONLINE`, `OFFLINE`, `ERROR`, `BUSY`).
5. **Resource Cleanup**: Ensure proper cleanup in the `disconnect` method.
6. **Metadata**: Use metadata to store device-specific configuration and capabilities.
7. **Command Interface**: Implement a consistent command interface through the `execute_command` method.
