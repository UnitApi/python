"""
device_discovery.py
"""

import asyncio
import logging
import socket
import json
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.devices.base import BaseDevice, DeviceStatus
from unitapi.protocols.websocket import WebSocketProtocol


class DeviceDiscoveryService:
    """
    Advanced device discovery and management service.
    """

    def __init__(
            self,
            server_host: str = '0.0.0.0',
            server_port: int = 7890,
            discovery_port: int = 7891
    ):
        """
        Initialize device discovery service.

        :param server_host: Host for UnitAPI server
        :param server_port: Port for UnitAPI server
        :param discovery_port: Port for discovery broadcast
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI Server
        self.server = UnitAPIServer(host=server_host, port=server_port)

        # WebSocket Protocol
        self.websocket = WebSocketProtocol(
            host=server_host,
            port=server_port + 1
        )

        # Discovery configuration
        self.discovery_host = server_host
        self.discovery_port = discovery_port

        # Device registry
        self.devices: Dict[str, BaseDevice] = {}

        # Discovery methods
        self.discovery_methods = [
            self._udp_discovery,
            self._mdns_discovery,
            self._network_scan
        ]

    async def register_device(
            self,
            device_info: Dict[str, Any]
    ) -> Optional[BaseDevice]:
        """
        Register a discovered device.

        :param device_info: Device information dictionary
        :return: Registered device instance
        """
        try:
            # Generate unique device ID
            device_id = device_info.get(
                'device_id',
                f"{device_info.get('type', 'unknown')}_{len(self.devices)}"
            )

            # Create base device
            device = BaseDevice(
                device_id=device_id,
                name=device_info.get('name', 'Unnamed Device'),
                device_type=device_info.get('type', 'generic'),
                metadata=device_info.get('metadata', {})
            )

            # Connect device
            await device.connect()

            # Register on server
            self.server.register_device(
                device_id=device.device_id,
                device_type=device.type,
                metadata=device.metadata
            )

            # Store in registry
            self.devices[device.device_id] = device

            self.logger.info(f"Registered device: {device.device_id}")
            return device

        except Exception as e:
            self.logger.error(f"Device registration failed: {e}")
            return None

    async def _udp_discovery(self) -> List[Dict[str, Any]]:
        """
        UDP broadcast device discovery.

        :return: List of discovered devices
        """
        discovered_devices = []

        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Broadcast discovery message
            message = json.dumps({
                'action': 'discover',
                'source': socket.gethostname()
            }).encode()

            sock.sendto(message, ('<broadcast>', self.discovery_port))

            # Listen for responses
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    device_info = json.loads(data.decode())
                    device_info['source_ip'] = addr[0]
                    discovered_devices.append(device_info)
                except socket.timeout:
                    break

        except Exception as e:
            self.logger.error(f"UDP discovery error: {e}")

        return discovered_devices

    async def _mdns_discovery(self) -> List[Dict[str, Any]]:
        """
        Simulated mDNS (Bonjour/Zeroconf) device discovery.

        :return: List of discovered devices
        """
        discovered_devices = []

        try:
            # In a real implementation, use zeroconf library
            # This is a simulated discovery
            simulated_devices = [
                {
                    'device_id': 'sensor_living_room',
                    'name': 'Living Room Sensor',
                    'type': 'sensor',
                    'metadata': {
                        'location': 'living room',
                        'capabilities': ['temperature', 'humidity']
                    }
                },
                {
                    'device_id': 'camera_entrance',
                    'name': 'Entrance Camera',
                    'type': 'camera',
                    'metadata': {
                        'location': 'entrance',
                        'resolution': '1080p'
                    }
                }
            ]

            discovered_devices.extend(simulated_devices)

        except Exception as e:
            self.logger.error(f"mDNS discovery error: {e}")

        return discovered_devices

    async def _network_scan(
            self,
            network_range: str = '192.168.1.0/24'
    ) -> List[Dict[str, Any]]:
        """
        Perform network scanning for devices.

        :param network_range: Network range to scan
        :return: List of discovered devices
        """
        discovered_devices = []

        try:
            import ipaddress
            import asyncio

            # Parse network range
            network = ipaddress.ip_network(network_range, strict=False)

            # Async port scanning function
            async def scan_host(ip):
                try:
                    # Simulated port scan for common device ports
                    ports_to_check = [80, 443, 554, 8080]
                    for port in ports_to_check:
                        try:
                            reader, writer = await asyncio.wait_for(
                                asyncio.open_connection(str(ip), port),
                                timeout=1.0
                            )
                            writer.close()
                            await writer.wait_closed()

                            # If connection successful, consider it a potential device
                            discovered_devices.append({
                                'device_id': f'net