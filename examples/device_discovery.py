import asyncio
import logging
import socket
import json
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.devices.base import BaseDevice, DeviceStatus
from unitapi.protocols.websocket import WebSocketProtocol


from unitapi.devices.camera import CameraDevice
from unitapi.devices.microphone import MicrophoneDevice
from unitapi.devices.remote_speaker_device import RemoteSpeakerDevice

class DeviceDiscoveryService:
    """
    Advanced device discovery and management service.
    """

    def __init__(
            self,
            server_host: str = '0.0.0.0',
            server_port: int = 7890,
            discovery_port: int = 7891,
            debug: bool = False
    ):
        """
        Initialize device discovery service.

        :param server_host: Host for UnitAPI server
        :param server_port: Port for UnitAPI server
        :param discovery_port: Port for discovery broadcast
        :param debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if debug:
            self.logger.info("Debug logging enabled")

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
            self._discover_local_devices,  # Add local device discovery
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
        Real mDNS (Bonjour/Zeroconf) device discovery using AsyncZeroconf.

        :return: List of discovered devices
        """
        discovered_devices = []

        try:
            from zeroconf.asyncio import AsyncZeroconf
            from zeroconf import ServiceBrowser, ServiceStateChange
            import socket
            
            self.logger.info("Starting mDNS discovery...")
            
            # Initialize AsyncZeroconf
            aiozc = AsyncZeroconf()
            zc = aiozc.zeroconf
            
            # Define service state change handler
            async def on_service_state_change(zc, service_type, name, state_change):
                if state_change is ServiceStateChange.Added:
                    self.logger.debug(f"Service {name} of type {service_type} found")
                    info = await aiozc.async_get_service_info(service_type, name)
                    if info:
                        # Extract IP address
                        addresses = [socket.inet_ntoa(addr) for addr in info.addresses]
                        ip_address = addresses[0] if addresses else None
                        
                        # Extract service name and remove type part
                        service_name = name.split('.')[0]
                        
                        # Extract properties
                        properties = {}
                        for key, value in info.properties.items():
                            if isinstance(key, bytes):
                                key = key.decode('utf-8')
                            if isinstance(value, bytes):
                                value = value.decode('utf-8')
                            properties[key] = value
                        
                        self.logger.debug(f"Service details - Name: {service_name}, IP: {ip_address}, Port: {info.port}")
                        
                        # Determine device type based on service type
                        device_type = 'generic'
                        if '_camera' in service_type or 'cam' in service_type.lower():
                            device_type = 'camera'
                        elif '_sensor' in service_type or 'sensor' in service_type.lower():
                            device_type = 'sensor'
                        elif '_speaker' in service_type or 'audio' in service_type.lower():
                            device_type = 'speaker'
                        elif '_googlecast' in service_type:
                            device_type = 'chromecast'
                        elif '_airplay' in service_type:
                            device_type = 'airplay'
                        elif '_ipp' in service_type:
                            device_type = 'printer'
                        
                        # Create device info
                        device_info = {
                            'device_id': f"mdns_{service_name}_{ip_address}".replace('.', '_'),
                            'name': service_name,
                            'type': device_type,
                            'metadata': {
                                'ip': ip_address,
                                'port': info.port,
                                'properties': properties,
                                'service_type': service_type
                            }
                        }
                        
                        discovered_devices.append(device_info)
                        self.logger.info(f"Discovered mDNS device: {service_name} ({device_type})")
            
            # Common service types to look for
            service_types = [
                "_http._tcp.local.",
                "_https._tcp.local.",
                "_rtsp._tcp.local.",
                "_ssh._tcp.local.",
                "_device-info._tcp.local.",
                "_googlecast._tcp.local.",
                "_hap._tcp.local.",  # HomeKit
                "_spotify-connect._tcp.local.",
                "_airplay._tcp.local.",
                "_ipp._tcp.local.",  # Printers
                "_smb._tcp.local.",  # File sharing
                "_unitapi._tcp.local.",  # Custom UnitAPI services
                "_workstation._tcp.local.",  # Workstations
                "_companion-link._tcp.local.",  # Apple devices
                "_raop._tcp.local.",  # AirPlay
                "_sleep-proxy._udp.local.",  # Apple devices
                "_daap._tcp.local.",  # iTunes sharing
                "_home-sharing._tcp.local."  # Apple Home Sharing
            ]
            
            # Create browsers for each service type
            browsers = []
            for service_type in service_types:
                self.logger.debug(f"Browsing for service type: {service_type}")
                browser = ServiceBrowser(
                    zc, 
                    service_type, 
                    handlers=[lambda zc, stype, name, state_change: 
                             asyncio.create_task(on_service_state_change(zc, stype, name, state_change))]
                )
                browsers.append(browser)
            
            # Allow some time for discovery
            self.logger.info("Waiting for mDNS services to be discovered...")
            await asyncio.sleep(5)  # Increased discovery time
            
            # Clean up
            await aiozc.async_close()
            
            self.logger.info(f"mDNS discovery found {len(discovered_devices)} devices")
            
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
                                'device_id': f'network_device_{ip}',
                                'name': f'Device at {ip}',
                                'type': 'network',
                                'metadata': {
                                    'ip': str(ip),
                                    'open_port': port
                                }
                            })
                            break
                        except (asyncio.TimeoutError, ConnectionRefusedError):
                            continue
                except Exception:
                    pass

            # Create tasks for each IP
            tasks = [
                scan_host(ip)
                for ip in network.hosts()
            ]

            # Run scans concurrently
            await asyncio.gather(*tasks)

        except Exception as e:
            self.logger.error(f"Network scan error: {e}")

        return discovered_devices

    async def _discover_local_devices(self) -> List[Dict[str, Any]]:
        """
        Discover local hardware devices (cameras, microphones, speakers).
        
        :return: List of discovered local devices
        """
        discovered_devices = []
        
        # Discover local cameras
        try:
            cameras = await self._discover_local_cameras()
            discovered_devices.extend(cameras)
        except Exception as e:
            self.logger.error(f"Local camera discovery error: {e}")
            
        # Discover local microphones
        try:
            microphones = await self._discover_local_microphones()
            discovered_devices.extend(microphones)
        except Exception as e:
            self.logger.error(f"Local microphone discovery error: {e}")
            
        # Discover local speakers
        try:
            speakers = await self._discover_local_speakers()
            discovered_devices.extend(speakers)
        except Exception as e:
            self.logger.error(f"Local speaker discovery error: {e}")
            
        return discovered_devices
        
    async def _discover_local_cameras(self) -> List[Dict[str, Any]]:
        """
        Discover local camera devices.
        
        :return: List of discovered camera devices
        """
        discovered_cameras = []
        
        # Method 1: Try to use OpenCV to detect cameras
        try:
            import cv2
            
            # Check for available camera indices (typically 0 for built-in, 1+ for external)
            for camera_idx in range(5):  # Check first 5 potential camera indices
                try:
                    cap = cv2.VideoCapture(camera_idx)
                    if cap.isOpened():
                        # Get camera properties
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        
                        # Release the camera
                        cap.release()
                        
                        # Create device info
                        camera_type = "internal" if camera_idx == 0 else "external"
                        device_info = {
                            'device_id': f"camera_{camera_idx}",
                            'name': f"Camera {camera_idx} ({camera_type})",
                            'type': 'camera',
                            'metadata': {
                                'index': camera_idx,
                                'resolution': f"{width}x{height}",
                                'fps': fps,
                                'camera_type': camera_type
                            }
                        }
                        
                        discovered_cameras.append(device_info)
                        self.logger.info(f"Discovered local camera: {device_info['name']}")
                except Exception as e:
                    self.logger.debug(f"No camera at index {camera_idx}: {e}")
        except ImportError:
            self.logger.warning("OpenCV not available for camera detection")
        
        # Method 2: If no cameras found with OpenCV, try to detect using system information
        if not discovered_cameras:
            try:
                import os
                import glob
                
                # Linux: Check for video devices in /dev
                if os.path.exists('/dev'):
                    video_devices = glob.glob('/dev/video*')
                    for i, device_path in enumerate(video_devices):
                        try:
                            device_num = int(device_path.replace('/dev/video', ''))
                            camera_type = "internal" if device_num == 0 else "external"
                            
                            device_info = {
                                'device_id': f"camera_{device_num}",
                                'name': f"Camera {device_num} ({camera_type})",
                                'type': 'camera',
                                'metadata': {
                                    'index': device_num,
                                    'device_path': device_path,
                                    'camera_type': camera_type
                                }
                            }
                            
                            discovered_cameras.append(device_info)
                            self.logger.info(f"Discovered system camera: {device_info['name']} at {device_path}")
                        except Exception as e:
                            self.logger.debug(f"Error processing video device {device_path}: {e}")
            except Exception as e:
                self.logger.debug(f"Error during system camera detection: {e}")
        
        # Method 3: If still no cameras found, create a virtual camera for testing
        if not discovered_cameras:
            self.logger.info("No physical cameras detected, creating virtual camera for testing")
            device_info = {
                'device_id': "camera_virtual",
                'name': "Virtual Camera",
                'type': 'camera',
                'metadata': {
                    'index': 0,
                    'resolution': "640x480",
                    'fps': 30,
                    'camera_type': "virtual"
                }
            }
            discovered_cameras.append(device_info)
        return discovered_cameras
        
    async def _discover_local_microphones(self) -> List[Dict[str, Any]]:
        """
        Discover local microphone devices.
        
        :return: List of discovered microphone devices
        """
        discovered_microphones = []
        
        try:
            # Try to use PyAudio to detect microphones
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Iterate through all audio devices
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                
                # Check if this is an input device (microphone)
                if device_info.get('maxInputChannels') > 0:
                    device_name = device_info.get('name')
                    channels = device_info.get('maxInputChannels')
                    sample_rate = int(device_info.get('defaultSampleRate'))
                    
                    # Create device info
                    mic_info = {
                        'device_id': f"microphone_{i}",
                        'name': device_name,
                        'type': 'microphone',
                        'metadata': {
                            'index': i,
                            'channels': channels,
                            'sample_rate': sample_rate
                        }
                    }
                    
                    discovered_microphones.append(mic_info)
                    self.logger.info(f"Discovered local microphone: {device_name}")
            
            # Clean up
            p.terminate()
                    
        except ImportError:
            self.logger.warning("PyAudio not available for microphone detection")
            
        return discovered_microphones
        
    async def _discover_local_speakers(self) -> List[Dict[str, Any]]:
        """
        Discover local speaker devices.
        
        :return: List of discovered speaker devices
        """
        discovered_speakers = []
        
        try:
            # Try to use PyAudio to detect speakers (output devices)
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Iterate through all audio devices
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                
                # Check if this is an output device (speaker)
                if device_info.get('maxOutputChannels') > 0:
                    device_name = device_info.get('name')
                    channels = device_info.get('maxOutputChannels')
                    sample_rate = int(device_info.get('defaultSampleRate'))
                    
                    # Create device info
                    speaker_info = {
                        'device_id': f"speaker_{i}",
                        'name': device_name,
                        'type': 'speaker',
                        'metadata': {
                            'index': i,
                            'channels': channels,
                            'sample_rate': sample_rate
                        }
                    }
                    
                    discovered_speakers.append(speaker_info)
                    self.logger.info(f"Discovered local speaker: {device_name}")
            
            # Clean up
            p.terminate()
                    
        except ImportError:
            self.logger.warning("PyAudio not available for speaker detection")
            
        return discovered_speakers

    async def discover_devices(self) -> List[BaseDevice]:
        """
        Perform comprehensive device discovery.

        :return: List of discovered and registered devices
        """
        discovered_devices = []

        # Run all discovery methods
        for method in self.discovery_methods:
            try:
                devices = await method()
                for device_info in devices:
                    registered_device = await self.register_device(device_info)
                    if registered_device:
                        discovered_devices.append(registered_device)
            except Exception as e:
                self.logger.error(f"Discovery method failed: {e}")

        return discovered_devices

    async def start(self):
        """
        Start device discovery service.
        """
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())

        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())

        # Perform device discovery
        await self.discover_devices()

        self.logger.info("Device Discovery Service started")

        # Wait for servers
        await asyncio.gather(server_task, websocket_task)


async def main():
    """
    Demonstrate device discovery capabilities.
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='UnitAPI Device Discovery Service')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Host for UnitAPI server')
    parser.add_argument('--port', type=int, default=7890, help='Port for UnitAPI server')
    parser.add_argument('--discovery-port', type=int, default=7891, help='Port for discovery broadcast')
    parser.add_argument('--network-range', default='192.168.1.0/24', help='Network range to scan')
    
    args = parser.parse_args()
    
    # Create discovery service
    discovery_service = DeviceDiscoveryService(
        server_host=args.host,
        server_port=args.port,
        discovery_port=args.discovery_port,
        debug=args.debug
    )
    
    # Override network range for network scan
    discovery_service._network_scan = lambda: discovery_service._network_scan.__wrapped__(
        discovery_service, args.network_range
    )

    try:
        # Start discovery
        await discovery_service.start()

    except Exception as e:
        print(f"Discovery service error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
