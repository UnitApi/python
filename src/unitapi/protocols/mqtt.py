"""
mqtt.py
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable


class MQTTProtocol:
    """
    MQTT protocol implementation for device communication.
    """

    def __init__(
            self,
            broker: str = 'localhost',
            port: int = 1883,
            client_id: Optional[str] = None
    ):
        """
        Initialize MQTT protocol handler.

        :param broker: MQTT broker address
        :param port: MQTT broker port
        :param client_id: Optional client identifier
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id or f'unitapi_client_{id(self)}'

        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = None
        self._subscriptions: Dict[str, Callable] = {}

    async def connect(self) -> bool:
        """
        Connect to MQTT broker.

        :return: Connection status
        """
        try:
            import paho.mqtt.asyncio as mqtt

            self._client = mqtt.Client(self.client_id)
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message

            await self._client.connect(self.broker, self.port)

            # Start the network loop
            self._client.loop_start()

            self.logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            return True

        except ImportError:
            self.logger.error("paho-mqtt not installed. Install with: pip install paho-mqtt")
            return False

        except Exception as e:
            self.logger.error(f"MQTT connection failed: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for successful connection.

        :param client: MQTT client instance
        :param userdata: User-defined data
        :param flags: Connection flags
        :param rc: Connection result code
        """
        if rc == 0:
            self.logger.info("MQTT broker connection successful")
        else:
            self.logger.error(f"Connection failed with code {rc}")

    def _on_message(self, client, userdata, message):
        """
        Callback for received messages.

        :param client: MQTT client instance
        :param userdata: User-defined data
        :param message: Received message
        """
        topic = message.topic
        payload = message.payload.decode()

        # Call registered handler for the topic
        if topic in self._subscriptions:
            try:
                self._subscriptions[topic](topic, payload)
            except Exception as e:
                self.logger.error(f"Error in message handler for {topic}: {e}")

    async def subscribe(self, topic: str, handler: Callable[[str, str], None]) -> bool:
        """
        Subscribe to an MQTT topic.

        :param topic: Topic to subscribe to
        :param handler: Callback function for received messages
        :return: Subscription status
        """
        try:
            if not self._client:
                await self.connect()

            self._client.subscribe(topic)
            self._subscriptions[topic] = handler

            self.logger.info(f"Subscribed to topic: {topic}")
            return True

        except Exception as e:
            self.logger.error(f"Subscription to {topic} failed: {e}")
            return False

    async def publish(self, topic: str, message: str) -> bool:
        """
        Publish a message to an MQTT topic.

        :param topic: Topic to publish to
        :param message: Message to send
        :return: Publish status
        """
        try:
            if not self._client:
                await self.connect()

            result = self._client.publish(topic, message)

            if result.rc == 0:
                self.logger.info(f"Message published to {topic}")
                return True
            else:
                self.logger.error(f"Failed to publish to {topic}")
                return False

        except Exception as e:
            self.logger.error(f"Publishing to {topic} failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from MQTT broker.

        :return: Disconnection status
        """
        try:
            if self._client:
                self._client.disconnect()
                self._client.loop_stop()

                self.logger.info("Disconnected from MQTT broker")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Disconnection failed: {e}")
            return False


# Example usage
async def main():
    """
    Demonstrate MQTT protocol usage.
    """
    # Create MQTT protocol handler
    mqtt_protocol = MQTTProtocol(broker='localhost', port=1883)

    # Define message handler
    def on_message(topic: str, message: str):
        print(f"Received message on {topic}: {message}")

    try:
        # Connect to broker
        await mqtt_protocol.connect()

        # Subscribe to a topic
        await mqtt_protocol.subscribe('unitapi/devices/#', on_message)

        # Publish a message
        await mqtt_protocol.publish('unitapi/devices/temperature', '22.5')

        # Keep connection open briefly
        await asyncio.sleep(5)

    finally:
        # Disconnect
        await mqtt_protocol.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())