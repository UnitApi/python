#!/usr/bin/env python3
"""
Remote Camera Capture Example

This script demonstrates how to capture images from cameras on remote devices.
"""

import asyncio
import argparse
import logging
import base64
import os
from typing import Optional, Dict, Any, List

from unitapi.core.client import UnitAPIClient
from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol


class RemoteCameraCaptureExample:
    def __init__(
            self,
            server_host: str = '0.0.0.0',
            server_port: int = 7890,
            client_host: str = 'localhost',
            client_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize remote camera capture example.

        Args:
            server_host: UnitAPI server host
            server_port: UnitAPI server port
            client_host: UnitAPI client host
            client_port: UnitAPI client port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI server
        self.server = UnitAPIServer(host=server_host, port=server_port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(
            host=server_host,
            port=server_port + 1
        )

        # UnitAPI client
        self.client = UnitAPIClient(
            server_host=client_host,
            server_port=client_port
        )
        
        # Remote devices
        self.remote_devices = {}

    async def start_server(self):
        """
        Start the UnitAPI server.
        """
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())

        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())
        
        self.logger.info(f"Server started on {self.server.host}:{self.server.port}")
        
        # Register local cameras
        await self.register_local_cameras()
        
        # Return tasks
        return [server_task, websocket_task]

    async def register_local_cameras(self):
        """
        Register local cameras with the server.
        """
        try:
            import cv2
            
            # Check for available camera indices
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
                        device_id = f"camera_{camera_idx}"
                        device_name = f"Camera {camera_idx} ({camera_type})"
                        
                        # Register with server
                        self.server.register_device(
                            device_id=device_id,
                            device_type='camera',
                            metadata={
                                'index': camera_idx,
                                'resolution': f"{width}x{height}",
                                'fps': fps,
                                'camera_type': camera_type,
                                'name': device_name
                            }
                        )
                        
                        self.logger.info(f"Registered local camera: {device_name}")
                except Exception as e:
                    self.logger.debug(f"No camera at index {camera_idx}: {e}")
                    
        except ImportError:
            self.logger.warning("OpenCV not available for camera detection")

    async def list_remote_cameras(self, remote_host: str) -> List[Dict[str, Any]]:
        """
        List cameras on a remote device.

        Args:
            remote_host: Remote host address

        Returns:
            List of camera devices
        """
        try:
            # Create client for remote host
            remote_client = UnitAPIClient(
                server_host=remote_host,
                server_port=7890  # Default port
            )
            
            # Get all devices
            devices = await remote_client.list_devices()
            
            # Filter for camera devices
            cameras = [
                device for device in devices
                if device.get('type') == 'camera'
            ]
            
            if cameras:
                self.logger.info(f"Found {len(cameras)} camera(s) on {remote_host}")
                for i, camera in enumerate(cameras):
                    camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
                    self.logger.info(f"Camera {i+1}: {camera.get('name')} ({camera_type}) (ID: {camera.get('device_id')})")
            else:
                self.logger.warning(f"No cameras found on {remote_host}")
                
            return cameras
            
        except Exception as e:
            self.logger.error(f"Failed to list cameras on {remote_host}: {e}")
            return []

    async def capture_from_remote_camera(
            self,
            remote_host: str,
            device_id: str,
            output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Capture an image from a camera on a remote device.

        Args:
            remote_host: Remote host address
            device_id: Camera device ID
            output_file: Optional path to save the image

        Returns:
            Capture result
        """
        try:
            # Create client for remote host
            remote_client = UnitAPIClient(
                server_host=remote_host,
                server_port=7890  # Default port
            )
            
            self.logger.info(f"Capturing image from device {device_id} on {remote_host}...")
            
            # Execute capture command
            result = await remote_client.execute_command(
                device_id=device_id,
                command='capture_image',
                params={}
            )
            
            if 'error' in result:
                self.logger.error(f"Capture failed: {result['error']}")
                return result
                
            self.logger.info("Image captured successfully")
            
            # Save to file if requested
            if output_file and 'image_data' in result:
                try:
                    # Decode base64 data if present
                    if isinstance(result['image_data'], str):
                        image_data = base64.b64decode(result['image_data'])
                    else:
                        image_data = result['image_data']
                        
                    # Determine file extension
                    _, ext = os.path.splitext(output_file)
                    if not ext:
                        output_file += '.jpg'
                        
                    # Save image file
                    with open(output_file, 'wb') as f:
                        f.write(image_data)
                            
                    self.logger.info(f"Image saved to {output_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save image: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to capture from remote device: {e}")
            return {'error': str(e)}

    async def capture_local_camera(
            self,
            camera_index: int = 0,
            output_file: str = 'camera_capture.jpg'
    ) -> bool:
        """
        Capture an image directly from a local camera using OpenCV.

        Args:
            camera_index: Camera device index
            output_file: Path to save the image

        Returns:
            Success status
        """
        try:
            import cv2
            
            self.logger.info(f"Opening camera {camera_index}...")
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                self.logger.error(f"Failed to open camera {camera_index}")
                return False
                
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.logger.info(f"Camera resolution: {width}x{height}")
            
            # Capture frame
            self.logger.info("Capturing frame...")
            ret, frame = cap.read()
            
            # Release the camera
            cap.release()
            
            if not ret:
                self.logger.error("Failed to capture frame")
                return False
                
            # Save the image
            cv2.imwrite(output_file, frame)
            self.logger.info(f"Image saved to {output_file}")
            
            return True
            
        except ImportError:
            self.logger.error("OpenCV not available for camera capture")
            return False
        except Exception as e:
            self.logger.error(f"Failed to capture from local camera: {e}")
            return False


async def run_server():
    """
    Run as a server to expose local cameras.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Remote Camera Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    example = RemoteCameraCaptureExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Start server
    tasks = await example.start_server()
    
    # Wait for server tasks
    await asyncio.gather(*tasks)


async def run_client():
    """
    Run as a client to capture from remote cameras.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Remote Camera Client')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--remote-host', required=True, help='Remote host address')
    parser.add_argument('--list', action='store_true', help='List remote cameras')
    parser.add_argument('--device-id', help='Remote camera device ID')
    parser.add_argument('--output', default='remote_capture.jpg', help='Output file path')
    
    args = parser.parse_args()
    
    example = RemoteCameraCaptureExample(
        debug=args.debug
    )
    
    if args.list:
        # List remote cameras
        await example.list_remote_cameras(args.remote_host)
    elif args.device_id:
        # Capture from remote camera
        await example.capture_from_remote_camera(
            remote_host=args.remote_host,
            device_id=args.device_id,
            output_file=args.output
        )
    else:
        # List and capture from first camera
        cameras = await example.list_remote_cameras(args.remote_host)
        
        if cameras:
            # Use the first camera
            camera = cameras[0]
            device_id = camera.get('device_id')
            camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
            
            output_file = args.output or f'remote_{camera_type}_capture.jpg'
            await example.capture_from_remote_camera(
                remote_host=args.remote_host,
                device_id=device_id,
                output_file=output_file
            )
        else:
            print(f"No cameras available on {args.remote_host}")


async def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Remote Camera Example')
    parser.add_argument('--server', action='store_true', help='Run as server')
    parser.add_argument('--client', action='store_true', help='Run as client')
    
    # Parse initial arguments
    args, remaining = parser.parse_known_args()
    
    if args.server:
        # Run as server
        await run_server()
    elif args.client:
        # Run as client
        await run_client()
    else:
        print("Please specify --server or --client mode")


if __name__ == "__main__":
    asyncio.run(main())
