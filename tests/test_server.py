"""
test_server.py
"""

import asyncio
import pytest
from unitapi.core.server import UnitAPIServer


@pytest.mark.asyncio
async def test_server_initialization():
    """
    Test UnitAPI server initialization.
    """
    server = UnitAPIServer(host='localhost', port=7890)

    # Check initial state
    assert server.host == 'localhost'
    assert server.port == 7890


@pytest.mark.asyncio
async def test_device_registration():
    """
    Test device registration functionality.
    """
    server = UnitAPIServer(host='localhost', port=7890)

    # Register a device
    device_info = {
        'device_id': 'test_device_01',
        'name': 'Test Device',
        'type': 'sensor',
        'metadata': {
            'location': 'test_lab'
        }
    }

    server.register_device(
        device_id=device_info['device_id'],
        device_type=device_info['type'],
        metadata=device_info['metadata']
    )

    # Check device registration
    devices = server.list_devices()
    assert device_info['device_id'] in devices
    assert devices[device_info['device_id']]['type'] == device_info['type']


@pytest.mark.asyncio
async def test_device_list_filtering():
    """
    Test device listing with type filtering.
    """
    server = UnitAPIServer(host='localhost', port=7890)

    # Register multiple devices
    devices_to_register = [
        {
            'device_id': 'sensor_01',
            'type': 'sensor',
            'metadata': {'location': 'room1'}
        },
        {
            'device_id': 'camera_01',
            'type': 'camera',
            'metadata': {'location': 'entrance'}
        }
    ]

    for device in devices_to_register:
        server.register_device(
            device_id=device['device_id'],
            device_type=device['type'],
            metadata=device['metadata']
        )

    # Filter sensor devices
    sensor_devices = server.list_devices(device_type='sensor')
    assert len(sensor_devices) == 1
    assert list(sensor_devices.keys())[0] == 'sensor_01'


@pytest.mark.asyncio
async def test_device_duplicate_registration():
    """
    Test handling of duplicate device registration.
    """
    server = UnitAPIServer(host='localhost', port=7890)

    device_info = {
        'device_id': 'unique_device',
        'type': 'test',
        'metadata': {'test': True}
    }

    # First registration should succeed
    server.register_device(
        device_id=device_info['device_id'],
        device_type=device_info['type'],
        metadata=device_info['metadata']
    )

    # Second registration with same ID should raise an exception
    with pytest.raises(ValueError):
        server.register_device(
            device_id=device_info['device_id'],
            device_type=device_info['type'],
            metadata=device_info['metadata']
        )

# Add more test cases as needed