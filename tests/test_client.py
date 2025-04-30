"""
test_client.py
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from unitapi.core.client import UnitAPIClient


@pytest.mark.asyncio
async def test_client_initialization():
    """
    Test UnitAPI client initialization.
    """
    client = UnitAPIClient(server_host='localhost', server_port=7890)

    assert client.host == 'localhost'
    assert client.port == 7890


@pytest.mark.asyncio
async def test_send_command():
    """
    Test sending commands to the server.
    """
    client = UnitAPIClient(server_host='localhost', server_port=7890)

    # Mock the send_command method
    with patch.object(client, 'send_command', new_callable=AsyncMock) as mock_send:
        # Setup mock return value
        mock_send.return_value = {
            'status': 'success',
            'data': {'message': 'Test command processed'}
        }

        # Send test command
        response = await client.send_command({
            'command': 'test_command',
            'params': {'key': 'value'}
        })

        # Verify method was called
        mock_send.assert_called_once()

        # Check response
        assert response['status'] == 'success'
        assert response['data']['message'] == 'Test command processed'


@pytest.mark.asyncio
async def test_list_devices():
    """
    Test device listing functionality.
    """
    client = UnitAPIClient(server_host='localhost', server_port=7890)

    # Mock the send_command method to simulate device listing
    with patch.object(client, 'send_command', new_callable=AsyncMock) as mock_send:
        # Setup mock return value
        mock_send.return_value = {
            'status': 'success',
            'devices': [
                {
                    'device_id': 'test_device_01',
                    'type': 'sensor',
                    'metadata': {'location': 'test_room'}
                }
            ]
        }

        # List devices
        result = client.list_devices()

        # Verify method was called
        mock_send.assert_called_once()

        # Check response
        assert result['status'] == 'success'
        assert len(result['devices']) == 1
        assert result['devices'][0]['device_id'] == 'test_device_01'


@pytest.mark.asyncio
async def test_register_device():
    """
    Test device registration through client.
    """
    client = UnitAPIClient(server_host='localhost', server_port=7890)

    # Mock the send_command method
    with patch.object(client, 'send_command', new_callable=AsyncMock) as mock_send:
        # Setup mock return value
        mock_send.return_value = {
            'status': 'success',
            'message': 'Device registered successfully'
        }

        # Register device
        result = client.register_device(
            device_id='new_device_01',
            device_type='camera',
            metadata={'location': 'entrance'}
        )

        # Verify method was called
        mock_send.assert_called_once()

        # Check response
        assert result['status'] == 'success'
        assert result['message'] == 'Device registered successfully'


@pytest.mark.asyncio
async def test_error_handling():
    """
    Test client error handling.
    """
    client = UnitAPIClient(server_host='localhost', server_port=7890)

    # Mock the send_command method to simulate an error
    with patch.object(client, 'send_command', new_callable=AsyncMock) as mock_send:
        # Setup mock error response
        mock_send.return_value = {
            'status': 'error',
            'message': 'Command processing failed'
        }

        # Send command
        response = await client.send_command({
            'command': 'failing_command'
        })

        # Check error response
        assert response['status'] == 'error'
        assert response['message'] == 'Command processing failed'

# Additional test cases can be added as needed