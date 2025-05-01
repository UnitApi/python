"""
UnitAPI Local Devices Manager

This module provides management functionality for local devices.
"""

import logging
import threading
from typing import Dict, Any, List, Optional

from ..core.mcp import MCPBroker, MCPClient
from ..devices.base import BaseDevice
from ..devices.keyboard import KeyboardDevice as Keyboard
from ..devices.mouse import MouseDevice as Mouse
from ..devices.camera import CameraDevice as Camera
from ..devices.microphone import MicrophoneDevice as Microphone
from ..devices.touchscreen import TouchscreenDevice as Touchscreen
from ..devices.gamepad import GamepadDevice as Gamepad
from ..devices.gpio import GPIODevice as GPIO

logger = logging.getLogger("unitapi.device_managers.local")

class LocalDevicesManager:
    """Manages local devices."""
    
    def __init__(self, config: Dict[str, Any], mcp_broker: MCPBroker):
        """
        Initialize the local devices manager.
        
        Args:
            config: The configuration dictionary
            mcp_broker: The MCP broker
        """
        self.config = config
        self.mcp_broker = mcp_broker
        self.mcp_client = MCPClient(mcp_broker, client_id="local_devices_manager")
        self.devices = {}
        self.running = False
        self.lock = threading.RLock()
        
        # Subscribe to device discovery requests
        self.mcp_client.subscribe("devices/discover", self._handle_discover)
        
        logger.debug("Local devices manager initialized")
    
    def start(self):
        """Start the local devices manager."""
        with self.lock:
            if self.running:
                logger.warning("Local devices manager already running")
                return
            
            self.running = True
            
            # Initialize devices from config
            self._init_devices()
            
            # Start devices
            for device_id, device in self.devices.items():
                try:
                    device.start()
                    logger.info(f"Started local device: {device_id}")
                except Exception as e:
                    logger.error(f"Error starting local device {device_id}: {e}")
            
            logger.info("Local devices manager started")
    
    def stop(self):
        """Stop the local devices manager."""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            
            # Stop devices
            for device_id, device in self.devices.items():
                try:
                    device.stop()
                    logger.info(f"Stopped local device: {device_id}")
                except Exception as e:
                    logger.error(f"Error stopping local device {device_id}: {e}")
            
            # Close MCP client
            self.mcp_client.close()
            
            logger.info("Local devices manager stopped")
    
    def _init_devices(self):
        """Initialize devices from configuration."""
        devices_config = self.config.get("devices", {}).get("local", {})
        
        # Initialize keyboard devices
        for device_id, device_config in devices_config.get("keyboard", {}).items():
            try:
                device = Keyboard(device_id, device_config, self.mcp_broker)
                self.devices[f"keyboard_{device_id}"] = device
                logger.debug(f"Initialized local keyboard device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local keyboard device {device_id}: {e}")
        
        # Initialize mouse devices
        for device_id, device_config in devices_config.get("mouse", {}).items():
            try:
                device = Mouse(device_id, device_config, self.mcp_broker)
                self.devices[f"mouse_{device_id}"] = device
                logger.debug(f"Initialized local mouse device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local mouse device {device_id}: {e}")
        
        # Initialize camera devices
        for device_id, device_config in devices_config.get("camera", {}).items():
            try:
                device = Camera(device_id, device_config, self.mcp_broker)
                self.devices[f"camera_{device_id}"] = device
                logger.debug(f"Initialized local camera device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local camera device {device_id}: {e}")
        
        # Initialize microphone devices
        for device_id, device_config in devices_config.get("microphone", {}).items():
            try:
                device = Microphone(device_id, device_config, self.mcp_broker)
                self.devices[f"microphone_{device_id}"] = device
                logger.debug(f"Initialized local microphone device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local microphone device {device_id}: {e}")
        
        # Initialize touchscreen devices
        for device_id, device_config in devices_config.get("touchscreen", {}).items():
            try:
                device = Touchscreen(device_id, device_config, self.mcp_broker)
                self.devices[f"touchscreen_{device_id}"] = device
                logger.debug(f"Initialized local touchscreen device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local touchscreen device {device_id}: {e}")
        
        # Initialize gamepad devices
        for device_id, device_config in devices_config.get("gamepad", {}).items():
            try:
                device = Gamepad(device_id, device_config, self.mcp_broker)
                self.devices[f"gamepad_{device_id}"] = device
                logger.debug(f"Initialized local gamepad device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local gamepad device {device_id}: {e}")
        
        # Initialize GPIO devices
        for device_id, device_config in devices_config.get("gpio", {}).items():
            try:
                device = GPIO(device_id, device_config, self.mcp_broker)
                self.devices[f"gpio_{device_id}"] = device
                logger.debug(f"Initialized local GPIO device: {device_id}")
            except Exception as e:
                logger.error(f"Error initializing local GPIO device {device_id}: {e}")
    
    def _handle_discover(self, message: Dict[str, Any]):
        """
        Handle device discovery requests.
        
        Args:
            message: The discovery request message
        """
        if not self.running:
            return
        
        # Get device type filter
        data = message.get("data", {})
        device_type = data.get("type")
        
        # Collect device information
        devices_info = []
        for device_id, device in self.devices.items():
            # Filter by device type if specified
            if device_type and not device_id.startswith(f"{device_type}_"):
                continue
            
            try:
                info = device.get_info()
                devices_info.append(info)
            except Exception as e:
                logger.error(f"Error getting info for device {device_id}: {e}")
        
        # Publish discovery response
        self.mcp_client.publish(
            "devices/discover/response",
            {
                "request_id": data.get("request_id"),
                "devices": devices_info
            }
        )
