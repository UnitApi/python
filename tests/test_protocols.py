"""
Tests for the protocol implementations in UnitAPI.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.unitapi.protocols.mqtt import MQTTProtocol
from src.unitapi.protocols.websocket import WebSocketProtocol


class TestMQTTProtocol:
    """Test cases for the MQTT protocol implementation."""

    @pytest.fixture
    def mqtt_protocol(self):
        """Create an MQTT protocol instance for testing."""
        return MQTTProtocol(broker="test-broker", port=1883, client_id="test-client")

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_connect_success(self, mock_mqtt, mqtt_protocol):
        """Test successful connection to MQTT broker."""
        # Setup mock
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client

        # Call connect
        result = await mqtt_protocol.connect()

        # Assertions
        assert result is True
        mock_mqtt.Client.assert_called_once_with("test-client")
        mock_client.connect.assert_called_once_with("test-broker", 1883)
        mock_client.loop_start.assert_called_once()

    @patch("src.unitapi.protocols.mqtt.mqtt", None)
    async def test_connect_import_error(self, mqtt_protocol):
        """Test connection failure due to missing paho-mqtt package."""
        # Call connect
        result = await mqtt_protocol.connect()

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_connect_exception(self, mock_mqtt, mqtt_protocol):
        """Test connection failure due to exception."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection failed")

        # Call connect
        result = await mqtt_protocol.connect()

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_on_connect_success(self, mock_mqtt, mqtt_protocol):
        """Test on_connect callback with successful connection."""
        # Setup
        await mqtt_protocol.connect()

        # Call on_connect with rc=0 (success)
        mqtt_protocol._on_connect(None, None, None, 0)

        # No assertions needed, just checking it doesn't raise exceptions

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_on_connect_failure(self, mock_mqtt, mqtt_protocol):
        """Test on_connect callback with failed connection."""
        # Setup
        await mqtt_protocol.connect()

        # Call on_connect with rc=1 (failure)
        mqtt_protocol._on_connect(None, None, None, 1)

        # No assertions needed, just checking it doesn't raise exceptions

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_on_message(self, mock_mqtt, mqtt_protocol):
        """Test on_message callback."""
        # Setup
        await mqtt_protocol.connect()

        # Create a mock handler
        mock_handler = MagicMock()
        mqtt_protocol._subscriptions["test/topic"] = mock_handler

        # Create a mock message
        mock_message = MagicMock()
        mock_message.topic = "test/topic"
        mock_message.payload.decode.return_value = "test-payload"

        # Call on_message
        mqtt_protocol._on_message(None, None, mock_message)

        # Assertions
        mock_handler.assert_called_once_with("test/topic", "test-payload")

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_on_message_exception(self, mock_mqtt, mqtt_protocol):
        """Test on_message callback with handler raising exception."""
        # Setup
        await mqtt_protocol.connect()

        # Create a mock handler that raises an exception
        mock_handler = MagicMock(side_effect=Exception("Handler error"))
        mqtt_protocol._subscriptions["test/topic"] = mock_handler

        # Create a mock message
        mock_message = MagicMock()
        mock_message.topic = "test/topic"
        mock_message.payload.decode.return_value = "test-payload"

        # Call on_message
        mqtt_protocol._on_message(None, None, mock_message)

        # Assertions
        mock_handler.assert_called_once_with("test/topic", "test-payload")
        # No exception should be raised

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_subscribe_success(self, mock_mqtt, mqtt_protocol):
        """Test successful subscription to a topic."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        await mqtt_protocol.connect()

        # Create a mock handler
        mock_handler = MagicMock()

        # Call subscribe
        result = await mqtt_protocol.subscribe("test/topic", mock_handler)

        # Assertions
        assert result is True
        mock_client.subscribe.assert_called_once_with("test/topic")
        assert mqtt_protocol._subscriptions["test/topic"] == mock_handler

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_subscribe_exception(self, mock_mqtt, mqtt_protocol):
        """Test subscription failure due to exception."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        mock_client.subscribe.side_effect = Exception("Subscription failed")
        await mqtt_protocol.connect()

        # Create a mock handler
        mock_handler = MagicMock()

        # Call subscribe
        result = await mqtt_protocol.subscribe("test/topic", mock_handler)

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_publish_success(self, mock_mqtt, mqtt_protocol):
        """Test successful message publication."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client

        # Setup publish result
        mock_result = MagicMock()
        mock_result.rc = 0  # Success
        mock_client.publish.return_value = mock_result

        await mqtt_protocol.connect()

        # Call publish
        result = await mqtt_protocol.publish("test/topic", "test-message")

        # Assertions
        assert result is True
        mock_client.publish.assert_called_once_with("test/topic", "test-message")

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_publish_failure(self, mock_mqtt, mqtt_protocol):
        """Test message publication failure."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client

        # Setup publish result
        mock_result = MagicMock()
        mock_result.rc = 1  # Failure
        mock_client.publish.return_value = mock_result

        await mqtt_protocol.connect()

        # Call publish
        result = await mqtt_protocol.publish("test/topic", "test-message")

        # Assertions
        assert result is False
        mock_client.publish.assert_called_once_with("test/topic", "test-message")

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_publish_exception(self, mock_mqtt, mqtt_protocol):
        """Test message publication exception."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        mock_client.publish.side_effect = Exception("Publication failed")

        await mqtt_protocol.connect()

        # Call publish
        result = await mqtt_protocol.publish("test/topic", "test-message")

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_disconnect_success(self, mock_mqtt, mqtt_protocol):
        """Test successful disconnection."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        await mqtt_protocol.connect()

        # Call disconnect
        result = await mqtt_protocol.disconnect()

        # Assertions
        assert result is True
        mock_client.disconnect.assert_called_once()
        mock_client.loop_stop.assert_called_once()

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_disconnect_no_client(self, mock_mqtt, mqtt_protocol):
        """Test disconnection with no client."""
        # Call disconnect without connecting first
        result = await mqtt_protocol.disconnect()

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.mqtt.mqtt")
    async def test_disconnect_exception(self, mock_mqtt, mqtt_protocol):
        """Test disconnection exception."""
        # Setup
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client
        mock_client.disconnect.side_effect = Exception("Disconnection failed")

        await mqtt_protocol.connect()

        # Call disconnect
        result = await mqtt_protocol.disconnect()

        # Assertions
        assert result is False


class TestWebSocketProtocol:
    """Test cases for the WebSocket protocol implementation."""

    @pytest.fixture
    def websocket_protocol(self):
        """Create a WebSocket protocol instance for testing."""
        return WebSocketProtocol(host="localhost", port=8765)

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_connect_success(self, mock_websockets, websocket_protocol):
        """Test successful connection to WebSocket server."""
        # Setup mock
        mock_websocket = MagicMock()
        mock_websockets.connect.return_value = mock_websocket

        # Call connect
        result = await websocket_protocol.connect()

        # Assertions
        assert result is True
        mock_websockets.connect.assert_called_once_with("ws://localhost:8765")
        assert websocket_protocol._websocket == mock_websocket
        assert websocket_protocol._connection_event.is_set()

    @patch("src.unitapi.protocols.websocket.websockets", None)
    async def test_connect_import_error(self, websocket_protocol):
        """Test connection failure due to missing websockets package."""
        # Call connect
        result = await websocket_protocol.connect()

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_connect_exception(self, mock_websockets, websocket_protocol):
        """Test connection failure due to exception."""
        # Setup mock to raise exception
        mock_websockets.connect.side_effect = Exception("Connection failed")

        # Call connect
        result = await websocket_protocol.connect()

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_send_success(self, mock_websockets, websocket_protocol):
        """Test successful message sending."""
        # Setup
        mock_websocket = MagicMock()
        mock_websockets.connect.return_value = mock_websocket
        await websocket_protocol.connect()

        # Call send
        result = await websocket_protocol.send("test_type", {"key": "value"})

        # Assertions
        assert result is True
        mock_websocket.send.assert_called_once()
        # Check that the message contains the type and data
        sent_message = mock_websocket.send.call_args[0][0]
        assert "test_type" in sent_message
        assert "key" in sent_message

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_send_exception(self, mock_websockets, websocket_protocol):
        """Test message sending failure due to exception."""
        # Setup
        mock_websocket = MagicMock()
        mock_websockets.connect.return_value = mock_websocket
        mock_websocket.send.side_effect = Exception("Send failed")
        await websocket_protocol.connect()

        # Call send
        result = await websocket_protocol.send("test_type", {"key": "value"})

        # Assertions
        assert result is False

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_add_message_handler(self, mock_websockets, websocket_protocol):
        """Test adding a message handler."""
        # Setup
        mock_handler = MagicMock()

        # Call add_message_handler
        websocket_protocol.add_message_handler("test_type", mock_handler)

        # Assertions
        assert websocket_protocol._message_handlers["test_type"] == mock_handler

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_disconnect_success(self, mock_websockets, websocket_protocol):
        """Test successful disconnection."""
        # Setup
        mock_websocket = MagicMock()
        mock_websockets.connect.return_value = mock_websocket
        await websocket_protocol.connect()

        # Call disconnect
        result = await websocket_protocol.disconnect()

        # Assertions
        assert result is True
        mock_websocket.close.assert_called_once()

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_disconnect_no_websocket(self, mock_websockets, websocket_protocol):
        """Test disconnection with no websocket."""
        # Call disconnect without connecting first
        result = await websocket_protocol.disconnect()

        # Assertions
        assert result is True  # Should return True even if there's no websocket

    @patch("src.unitapi.protocols.websocket.websockets")
    async def test_disconnect_exception(self, mock_websockets, websocket_protocol):
        """Test disconnection exception."""
        # Setup
        mock_websocket = MagicMock()
        mock_websockets.connect.return_value = mock_websocket
        mock_websocket.close.side_effect = Exception("Disconnection failed")
        await websocket_protocol.connect()

        # Call disconnect
        result = await websocket_protocol.disconnect()

        # Assertions
        assert result is False
