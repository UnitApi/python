"""
remote_control.py
"""

import asyncio
import logging
from unitapi.core.server import UnitAPIServer
from unitapi.core.client import UnitAPIClient
from unitapi.devices.base import BaseDevice
from unitapi.security.authentication import AuthenticationManager


class RemoteControlExample:
    """
    Demonstrate remote device control using UnitAPI.
    """

    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890
    ):
        """
        Initialize remote control demonstration.

        :param server_host: Server host
        :param server_port: Server port
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create server and client
        self.server = UnitAPIServer(host=server_host, port=server_port)
        self.client = UnitAPIClient(server_host=server_host, server_port=server_port)

        # Authentication manager
        self.auth_manager = AuthenticationManager()

    async def setup_authentication(self):
        """
        Set up user authentication.
        """
        # Register admin user
        await self.auth_manager.register_user(
            username='admin',
            password='secure_password',
            roles=['admin', 'device_manager']
        )

        # Register regular user
        await self.auth_manager.register_user(
            username='user',
            password='user_password',
            roles=['user']
        )

    async def register_demo_devices(self):
        """
        Register demo devices for remote control.
        """
        demo_devices = [
            {
                'device_id': 'thermostat_01',
                'name': 'Living Room Thermostat',
                'type': 'climate',
                'metadata': {
                    'location': 'living_room',
                    'min_temp': 18,
                    'max_temp': 30
                }
            },
            {
                'device_id': 'light_01',
                'name': 'Kitchen Lights',
                'type': 'lighting',
                'metadata': {
                    'location': 'kitchen',
                    'dimmable': True
                }
            }
        ]

        # Register devices on server
        for device in demo_devices:
            self.server.register_device(
                device_id=device['device_id'],
                device_type=device['type'],
                metadata=device['metadata']
            )

    async def demonstrate_remote_control(self):
        """
        Demonstrate remote device control workflow.
        """
        # Start server
        server_task = asyncio.create_task(self.server.start())

        try:
            # Setup authentication
            await self.setup_authentication()

            # Register demo devices
            await self.register_demo_devices()

            # Authenticate admin user
            admin_token = await self.auth_manager.authenticate('admin', 'secure_password')

            # List available devices
            devices = self.client.list_devices()
            self.logger.info("Available Devices: %s", devices)

            # Execute commands on devices
            for device in devices:
                command_result = self.client.execute_command(
                    device_id=device['device_id'],
                    command='status',
                    params={'detail': True}
                )
                self.logger.info(f"Device {device['device_id']} Status: {command_result}")

        except Exception as e:
            self.logger.error(f"Remote control demonstration failed: {e}")

        finally:
            # Stop server
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass


async def main():
    """
    Run remote control demonstration.
    """
    demo = RemoteControlExample()
    await demo.demonstrate_remote_control()


if __name__ == "__main__":
    asyncio.run(main())