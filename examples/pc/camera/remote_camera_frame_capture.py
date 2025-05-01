#!/usr/bin/env python3
"""
Remote Camera Frame Capture Example

This script demonstrates how to capture a frame from a camera on a remote device.
"""

import asyncio
import argparse
import logging
import os
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List

from unitapi.core.client import UnitAPIClient


class RemoteCameraFrameCaptureExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize remote camera frame capture example.

        Args:
            server_host: UnitAPI server host
            server_port: UnitAPI server port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI client
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )

    async def list_remote_cameras(self) -> List[Dict[str, Any]]:
        """
        List available cameras on the remote device.

        Returns:
            List of camera devices
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for camera devices
            cameras = [
                device for device in devices
                if device.get('type') == 'camera'
            ]
            
            if cameras:
                self.logger.info(f"Found {len(cameras)} camera(s) on remote device")
                for i, camera in enumerate(cameras):
                    camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
                    self.logger.info(f"Camera {i+1}: {camera.get('name')} ({camera_type}) (ID: {camera.get('device_id')})")
            else:
                self.logger.warning("No cameras found on remote device")
                
            return cameras
            
        except Exception as e:
            self.logger.error(f"Failed to list remote cameras: {e}")
            return []

    async def capture_frame(
            self,
            device_id: str,
            output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Capture a frame from a remote camera.

        Args:
            device_id: Camera device ID
            output_file: Optional path to save the image. If None, a timestamped filename will be used.

        Returns:
            Capture result
        """
        # Generate default filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"remote_camera_{timestamp}.jpg"
            
        try:
            self.logger.info(f"Capturing frame from remote camera {device_id}...")
            
            # Execute capture command
            result = await self.client.execute_command(
                device_id=device_id,
                command='capture_image',
                params={}
            )
            
            if 'error' in result:
                self.logger.error(f"Capture failed: {result['error']}")
                return result
                
            self.logger.info("Frame captured successfully")
            
            # Save to file if image data is present
            if 'image_data' in result:
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
                            
                    self.logger.info(f"Frame saved to {output_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save image: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to capture from remote camera: {e}")
            return {'error': str(e)}

    async def start_video_stream(
            self,
            device_id: str,
            duration: int = 10
    ) -> Dict[str, Any]:
        """
        Start a video stream from a remote camera.

        Args:
            device_id: Camera device ID
            duration: Stream duration in seconds

        Returns:
            Stream start result
        """
        try:
            self.logger.info(f"Starting video stream from remote camera {device_id} for {duration} seconds...")
            
            # Execute start_stream command
            result = await self.client.execute_command(
                device_id=device_id,
                command='start_stream',
                params={'duration': duration}
            )
            
            if 'error' in result:
                self.logger.error(f"Stream start failed: {result['error']}")
                return result
                
            self.logger.info(f"Video stream started successfully (stream ID: {result.get('stream_id')})")
            
            # Wait for the stream to complete
            self.logger.info(f"Streaming for {duration} seconds...")
            await asyncio.sleep(duration)
            
            self.logger.info("Video stream completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to stream from remote camera: {e}")
            return {'error': str(e)}


async def main():
    """
    Run the remote camera frame capture example.
    """
    parser = argparse.ArgumentParser(description='Remote Camera Frame Capture Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='Remote UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='Remote UnitAPI server port')
    parser.add_argument('--list', action='store_true', help='List available remote cameras')
    parser.add_argument('--device-id', help='Specific remote camera device ID to use')
    parser.add_argument('--output', help='Output file path for captured frame')
    parser.add_argument('--stream', action='store_true', help='Start a video stream instead of capturing a single frame')
    parser.add_argument('--duration', type=int, default=10, help='Stream duration in seconds')
    
    args = parser.parse_args()
    
    example = RemoteCameraFrameCaptureExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    if args.list:
        # List available remote cameras
        await example.list_remote_cameras()
    elif args.device_id:
        if args.stream:
            # Start video stream
            await example.start_video_stream(
                device_id=args.device_id,
                duration=args.duration
            )
        else:
            # Capture frame
            await example.capture_frame(
                device_id=args.device_id,
                output_file=args.output
            )
    else:
        # List cameras and use the first one
        cameras = await example.list_remote_cameras()
        
        if cameras:
            # Use the first camera
            camera = cameras[0]
            device_id = camera.get('device_id')
            camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
            
            if args.stream:
                # Start video stream
                await example.start_video_stream(
                    device_id=device_id,
                    duration=args.duration
                )
            else:
                # Capture frame
                output_file = args.output or f"remote_{camera_type}_capture.jpg"
                await example.capture_frame(
                    device_id=device_id,
                    output_file=output_file
                )
        else:
            print("No remote cameras available. Make sure the UnitAPI server is running and has cameras registered.")
            print("You can start the device discovery service first with: python examples/device_discovery.py")


if __name__ == "__main__":
    asyncio.run(main())
