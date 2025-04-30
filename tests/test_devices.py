"""
test_devices.py
"""

import asyncio
import pytest
from unitapi.devices.base import SensorDevice, AudioDevice, GPIODevice
from unitapi.devices.microphone import MicrophoneDevice
from unitapi.devices.camera import CameraDevice
from unitapi.devices.gpio import GPIODevice


@pytest.mark.asyncio
async def test_base_sensor_device():
    """
    Test base sensor device functionality.
    """
    sensor = SensorDevice(
        device_id='test_sensor_01',
        name='Test Sensor',
        device_type='sensor',
        metadata={'location': 'test_room'}
    )

    # Check device initialization
    assert sensor.device_id == 'test_sensor_01'
    assert sensor.name == 'Test Sensor'
    assert sensor.type == 'sensor'
    assert sensor.metadata.get('location') == 'test_room'


@pytest.mark.asyncio
async def test_microphone_device():
    """
    Test microphone device specific functionality.
    """
    mic = MicrophoneDevice(
        device_id='mic_01',
        name='Test Microphone',
        metadata={'sample_rate': 44100}
    )

    # Connect device
    connected = await mic.connect()
    assert connected is True

    # Record audio
    audio_data = await mic.record_audio(duration=2, sample_rate=44100)

    # Validate audio data
    assert 'duration' in audio_data
    assert 'sample_rate' in audio_data
    assert 'data' in audio_data


@pytest.mark.asyncio
async def test_camera_device():
    """
    Test camera device specific functionality.
    """
    camera = CameraDevice(
        device_id='cam_01',
        name='Test Camera',
        metadata={'resolution': '1080p'}
    )

    # Connect device
    connected = await camera.connect()
    assert connected is True

    # Capture image
    image_data = await camera.capture_image()

    # Validate image data
    assert 'device_id' in image_data
    assert 'resolution' in image_data
    assert 'timestamp' in image_data
    assert 'image_data' in image_data


@pytest.mark.asyncio
async def test_gpio_device():
    """
    Test GPIO device functionality.
    """
    gpio = GPIODevice(
        device_id='gpio_01',
        name='Test GPIO Device',
        metadata={'total_pins': 40}
    )

    # Connect device
    connected = await gpio.connect()
    assert connected is True

    # Set pin mode
    pin_mode_result = await gpio.set_pin_mode(18, 'output')
    assert pin_mode_result['status'] == 'success'

    # Digital write
    write_result = await gpio.digital_write(18, True)
    assert write_result['status'] == 'success'

    # Digital read
    read_result = await gpio.digital_read(18)
    assert read_result['status'] == 'success'
    assert 'value' in read_result


@pytest.mark.asyncio
async def test_device_command_execution():
    """
    Test generic command execution across devices.
    """
    # Test camera device
    camera = CameraDevice(
        device_id='cam_test',
        name='Test Camera'
    )

    # Execute stream command
    stream_result = await camera.execute_command('start_stream', {'duration': 5})
    assert 'stream_id' in stream_result

    # Test microphone device
    mic = MicrophoneDevice(
        device_id='mic_test',
        name='Test Microphone'
    )

    # Execute record command
    record_result = await mic.execute_command('record', {'duration': 3})
    assert 'data' in record_result


@pytest.mark.asyncio
async def test_device_connection_lifecycle():
    """
    Test device connection and disconnection lifecycle.
    """
    # Create GPIO device
    gpio = GPIODevice(
        device_id='gpio_lifecycle',
        name='Lifecycle GPIO'
    )

    # Connect device
    connected = await gpio.connect()
    assert connected is True
    assert gpio.status.name == 'ONLINE'

    # Disconnect device
    disconnected = await gpio.disconnect()
    assert disconnected is True
    assert gpio.status.name == 'OFFLINE'

# Additional device-specific tests can be added as needed