"""
UnitAPI Network Devices Manager

This module provides management functionality for network devices.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional

from ..core.mcp import MCPBroker, MCPClient
from ..core.server import Server
from ..core.client import Client
from ..protocols.websocket import WebSocketProtocol

logger = logging.getLogger("unitapi.device_managers.network")


class NetworkDevicesManager:
    """Manages network devices."""

    def __init__(self, config: Dict[str, Any], mcp_broker: MCPBroker):
        """
        Initialize the network devices manager.

        Args:
            config: The configuration dictionary
            mcp_broker: The MCP broker
        """
        self.config = config
        self.mcp_broker = mcp_broker
        self.mcp_client = MCPClient(mcp_broker, client_id="network_devices_manager")
        self.servers = {}
        self.clients = {}
        self.running = False
        self.lock = threading.RLock()

        # Subscribe to device discovery requests
        self.mcp_client.subscribe("devices/discover/network", self._handle_discover)

        # Subscribe to connection status updates
        self.mcp_client.subscribe(
            "network/connection/+/status", self._handle_connection_status
        )

        logger.debug("Network devices manager initialized")

    def start(self):
        """Start the network devices manager."""
        with self.lock:
            if self.running:
                logger.warning("Network devices manager already running")
                return

            self.running = True

            # Initialize servers and clients from config
            self._init_servers()
            self._init_clients()

            # Start servers
            for server_id, server in self.servers.items():
                try:
                    server.start()
                    logger.info(f"Started network server: {server_id}")
                except Exception as e:
                    logger.error(f"Error starting network server {server_id}: {e}")

            # Start clients
            for client_id, client in self.clients.items():
                try:
                    client.connect()
                    logger.info(f"Started network client: {client_id}")
                except Exception as e:
                    logger.error(f"Error starting network client {client_id}: {e}")

            logger.info("Network devices manager started")

    def stop(self):
        """Stop the network devices manager."""
        with self.lock:
            if not self.running:
                return

            self.running = False

            # Stop clients
            for client_id, client in self.clients.items():
                try:
                    client.disconnect()
                    logger.info(f"Stopped network client: {client_id}")
                except Exception as e:
                    logger.error(f"Error stopping network client {client_id}: {e}")

            # Stop servers
            for server_id, server in self.servers.items():
                try:
                    server.stop()
                    logger.info(f"Stopped network server: {server_id}")
                except Exception as e:
                    logger.error(f"Error stopping network server {server_id}: {e}")

            # Close MCP client
            self.mcp_client.close()

            logger.info("Network devices manager stopped")

    def _init_servers(self):
        """Initialize servers from configuration."""
        servers_config = self.config.get("network", {}).get("servers", {})

        for server_id, server_config in servers_config.items():
            try:
                # Get protocol
                protocol_name = server_config.get("protocol", "websocket")
                protocol = self._create_protocol(protocol_name, server_config)

                # Create server
                server = Server(
                    server_id=server_id,
                    config=server_config,
                    protocol=protocol,
                    mcp_broker=self.mcp_broker,
                )

                self.servers[server_id] = server
                logger.debug(f"Initialized network server: {server_id}")
            except Exception as e:
                logger.error(f"Error initializing network server {server_id}: {e}")

    def _init_clients(self):
        """Initialize clients from configuration."""
        clients_config = self.config.get("network", {}).get("clients", {})

        for client_id, client_config in clients_config.items():
            try:
                # Get protocol
                protocol_name = client_config.get("protocol", "websocket")
                protocol = self._create_protocol(protocol_name, client_config)

                # Create client
                client = Client(
                    client_id=client_id,
                    config=client_config,
                    protocol=protocol,
                    mcp_broker=self.mcp_broker,
                )

                self.clients[client_id] = client
                logger.debug(f"Initialized network client: {client_id}")
            except Exception as e:
                logger.error(f"Error initializing network client {client_id}: {e}")

    def _create_protocol(self, protocol_name: str, config: Dict[str, Any]):
        """
        Create a protocol instance.

        Args:
            protocol_name: Name of the protocol
            config: Protocol configuration

        Returns:
            Protocol instance
        """
        if protocol_name == "websocket":
            return WebSocketProtocol(config)
        else:
            raise ValueError(f"Unsupported protocol: {protocol_name}")

    def _handle_discover(self, message: Dict[str, Any]):
        """
        Handle network device discovery requests.

        Args:
            message: The discovery request message
        """
        if not self.running:
            return

        # Get device type filter
        data = message.get("data", {})
        device_type = data.get("type")

        # Collect server information
        servers_info = []
        for server_id, server in self.servers.items():
            # Filter by device type if specified
            if device_type and not server_id.startswith(f"{device_type}_"):
                continue

            try:
                info = server.get_info()
                servers_info.append(info)
            except Exception as e:
                logger.error(f"Error getting info for server {server_id}: {e}")

        # Collect client information
        clients_info = []
        for client_id, client in self.clients.items():
            # Filter by device type if specified
            if device_type and not client_id.startswith(f"{device_type}_"):
                continue

            try:
                info = client.get_info()
                clients_info.append(info)
            except Exception as e:
                logger.error(f"Error getting info for client {client_id}: {e}")

        # Publish discovery response
        self.mcp_client.publish(
            "devices/discover/network/response",
            {
                "request_id": data.get("request_id"),
                "servers": servers_info,
                "clients": clients_info,
            },
        )

    def _handle_connection_status(self, message: Dict[str, Any]):
        """
        Handle connection status updates.

        Args:
            message: The status update message
        """
        if not self.running:
            return

        # Extract connection ID from topic
        topic = message.get("topic", "")
        parts = topic.split("/")
        if len(parts) < 4:
            return

        connection_id = parts[2]
        status = message.get("data", {}).get("status")

        if status == "disconnected":
            # Check if this is a client and attempt reconnection
            if connection_id in self.clients:
                client = self.clients[connection_id]

                # Check if auto-reconnect is enabled
                if client.config.get("auto_reconnect", True):
                    # Schedule reconnection attempt
                    reconnect_delay = client.config.get("reconnect_delay", 5)
                    logger.info(
                        f"Scheduling reconnection for client {connection_id} in {reconnect_delay} seconds"
                    )

                    def reconnect():
                        if self.running and connection_id in self.clients:
                            try:
                                logger.info(
                                    f"Attempting to reconnect client {connection_id}"
                                )
                                client.connect()
                            except Exception as e:
                                logger.error(
                                    f"Error reconnecting client {connection_id}: {e}"
                                )

                    # Start reconnection thread
                    threading.Timer(reconnect_delay, reconnect).start()
