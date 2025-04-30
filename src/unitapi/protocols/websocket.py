"""
websocket.py
"""

install
websockets
")
return False

except Exception as e:
self.logger.error(f"WebSocket connection failed: {e}")
return False


async def _receive_messages(self):
    """
    Continuously receive and process WebSocket messages.
    """
    try:
        while True:
            # Wait for a message
            message = await self._websocket.recv()

            try:
                # Parse JSON message
                data = json.loads(message)

                # Determine message type/route
                message_type = data.get('type')

                # Call appropriate handler
                if message_type in self._message_handlers:
                    await self._message_handlers[message_type](data)
                else:
                    self.logger.warning(f"No handler for message type: {message_type}")

            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON message: {message}")
            except Exception as handler_error:
                self.logger.error(f"Error processing message: {handler_error}")

    except websockets.ConnectionClosed:
        self.logger.info("WebSocket connection closed")
        self._connection_event.clear()
    except Exception as e:
        self.logger.error(f"Message receiving error: {e}")
        self._connection_event.clear()


async def send(self, message_type: str, data: Dict[str, Any]) -> bool:
    """
    Send a message via WebSocket.

    :param message_type: Type of message
    :param data: Message payload
    :return: Send status
    """
    try:
        # Wait for connection if not established
        await self._connection_event.wait()

        # Prepare message
        message = {
            'type': message_type,
            'timestamp': asyncio.get_event_loop().time(),
            **data
        }

        # Send message
        await self._websocket.send(json.dumps(message))

        self.logger.info(f"Sent message: {message_type}")
        return True

    except Exception as e:
        self.logger.error(f"Message sending failed: {e}")
        return False


def add_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], Any]):
    """
    Register a handler for specific message types.

    :param message_type: Type of message to handle
    :param handler: Async callback function
    """
    self._message_handlers[message_type] = handler
    self.logger.info(f"Registered handler for message type: {message_type}")


async def create_server(self) -> None:
    """
    Create a WebSocket server for device communication.
    """
    try:
        server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )

        self.logger.info(f"WebSocket server started on {self.host}:{self.port}")

        await server.wait_closed()

    except Exception as e:
        self.logger.error(f"WebSocket server creation failed: {e}")


async def _handle_client(self, websocket, path):
    """
    Handle incoming WebSocket client connections.

    :param websocket: WebSocket connection
    :param path: Connection path
    """
    try:
        self.logger.info(f"New client connected: {path}")

        async for message in websocket:
            try:
                # Parse incoming message
                data = json.loads(message)

                # Process message based on type
                response = await self._process_message(data)

                # Send response back to client
                await websocket.send(json.dumps(response))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'error': 'Invalid JSON',
                    'status': 'error'
                }))
            except Exception as e:
                await websocket.send(json.dumps({
                    'error': str(e),
                    'status': 'error'
                }))

    except websockets.ConnectionClosed:
        self.logger.info("Client connection closed")
    except Exception as e:
        self.logger.error(f"Client handling error: {e}")


async def _process_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incoming WebSocket messages.

    :param data: Parsed message data
    :return: Response data
    """
    message_type = data.get('type')

    if message_type == 'device_command':
        # Example device command processing
        device_id = data.get('device_id')
        command = data.get('command')
        params = data.get('params', {})

        # Simulated command execution
        return {
            'type': 'command_response',
            'device_id': device_id,
            'command': command,
            'status': 'success',
            'result': f"Command {command} processed for device {device_id}"
        }

    elif message_type == 'device_discovery':
        # Simulated device discovery
        return {
            'type': 'discovery_response',
            'devices': [
                {
                    'device_id': 'sensor_01',
                    'type': 'temperature',
                    'location': 'living_room'
                },
                {
                    'device_id': 'camera_01',
                    'type': 'camera',
                    'location': 'entrance'
                }
            ]
        }

    else:
        return {
            'error': f'Unsupported message type: {message_type}',
            'status': 'error'
        }


async def disconnect(self) -> bool:
    """
    Disconnect WebSocket connection.

    :return: Disconnection status
    """
    try:
        if self._websocket:
            await self._websocket.close()
            self.logger.info("WebSocket connection closed")
        return True
    except Exception as e:
        self.logger.error(f"Disconnection failed: {e}")
        return False


# Example usage
async def main():
    """
    Demonstrate WebSocket protocol usage.
    """
    # Create WebSocket protocol handler
    ws_protocol = WebSocketProtocol(host='localhost', port=8765)

    # Define message handlers
    def device_command_handler(data: Dict[str, Any]):
        print(f"Received device command: {data}")

    # Add message handler
    ws_protocol.add_message_handler('device_command', device_command_handler)

    try:
        # Connect to WebSocket server
        await ws_protocol.connect()

        # Send a device command
        await ws_protocol.send('device_command', {
            'device_id': 'sensor_01',
            'command': 'read_temperature'
        })

        # Keep connection open briefly
        await asyncio.sleep(5)

    finally:
        # Disconnect
        await ws_protocol.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())