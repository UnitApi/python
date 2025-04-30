#!/usr/bin/env python3
"""
Raspberry Pi Camera Module Example

This script demonstrates how to use the Raspberry Pi Camera Module with UnitAPI.
It shows how to capture images and video from the Raspberry Pi Camera Module.
"""

import asyncio
import argparse
import logging
import os
import base64
import time
from typing import Dict, Any, Optional, List

from unitapi.core.client import UnitAPIClient


class RPiCameraExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Camera example.

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
        
        # Camera device ID
        self.camera_device_id = None

    async def discover_camera(self) -> bool:
        """
        Discover Raspberry Pi Camera Module.

        Returns:
            Success status
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
                self.logger.info(f"Found {len(cameras)} camera(s)")
                for i, camera in enumerate(cameras):
                    camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
                    self.logger.info(f"Camera {i+1}: {camera.get('name')} ({camera_type}) (ID: {camera.get('device_id')})")
                
                # Look for Raspberry Pi camera specifically
                rpi_cameras = [
                    camera for camera in cameras
                    if 'raspberry' in camera.get('name', '').lower() or 
                       'rpi' in camera.get('name', '').lower() or
                       'raspberry' in str(camera.get('metadata', {})).lower() or
                       'rpi' in str(camera.get('metadata', {})).lower()
                ]
                
                if rpi_cameras:
                    # Use the first Raspberry Pi camera
                    self.camera_device_id = rpi_cameras[0].get('device_id')
                    self.logger.info(f"Using Raspberry Pi Camera: {rpi_cameras[0].get('name')}")
                else:
                    # Use the first available camera
                    self.camera_device_id = cameras[0].get('device_id')
                    self.logger.info(f"No specific Raspberry Pi Camera found. Using: {cameras[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No cameras found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover camera: {e}")
            return False

    async def capture_image(
            self,
            output_file: str = 'rpi_camera_capture.jpg',
            resolution: str = '1920x1080'
    ) -> Dict[str, Any]:
        """
        Capture an image from the Raspberry Pi Camera Module.

        Args:
            output_file: Path to save the image
            resolution: Image resolution (WxH)

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Capturing image from Raspberry Pi Camera at {resolution} resolution")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Execute capture command
            result = await self.client.execute_command(
                device_id=self.camera_device_id,
                command='capture_image',
                params={
                    'width': width,
                    'height': height,
                    'format': 'jpeg',
                    'quality': 90
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Image capture failed: {result['error']}")
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
            self.logger.error(f"Failed to capture image: {e}")
            return {'error': str(e)}

    async def capture_video(
            self,
            output_file: str = 'rpi_camera_video.mp4',
            duration: int = 5,
            resolution: str = '1280x720',
            fps: int = 30
    ) -> Dict[str, Any]:
        """
        Capture a video from the Raspberry Pi Camera Module.

        Args:
            output_file: Path to save the video
            duration: Recording duration in seconds
            resolution: Video resolution (WxH)
            fps: Frames per second

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Capturing {duration}s video at {resolution} ({fps} fps)")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Start video recording
            result = await self.client.execute_command(
                device_id=self.camera_device_id,
                command='start_video_recording',
                params={
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'format': 'h264',
                    'output_file': output_file
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Video recording start failed: {result['error']}")
                return result
                
            recording_id = result.get('recording_id')
            self.logger.info(f"Video recording started (ID: {recording_id})")
            
            # Wait for the specified duration
            self.logger.info(f"Recording for {duration} seconds...")
            await asyncio.sleep(duration)
            
            # Stop video recording
            stop_result = await self.client.execute_command(
                device_id=self.camera_device_id,
                command='stop_video_recording',
                params={
                    'recording_id': recording_id
                }
            )
            
            if 'error' in stop_result:
                self.logger.error(f"Video recording stop failed: {stop_result['error']}")
                return stop_result
                
            self.logger.info(f"Video recording stopped and saved to {output_file}")
            
            return stop_result
            
        except Exception as e:
            self.logger.error(f"Failed to capture video: {e}")
            return {'error': str(e)}

    async def capture_timelapse(
            self,
            output_dir: str = 'rpi_timelapse',
            interval: int = 2,
            count: int = 10,
            resolution: str = '1920x1080'
    ) -> Dict[str, Any]:
        """
        Capture a timelapse sequence from the Raspberry Pi Camera Module.

        Args:
            output_dir: Directory to save the timelapse images
            interval: Interval between captures in seconds
            count: Number of images to capture
            resolution: Image resolution (WxH)

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Starting timelapse: {count} images at {interval}s intervals")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Capture sequence of images
            for i in range(count):
                # Generate filename
                filename = os.path.join(output_dir, f"timelapse_{i:04d}.jpg")
                
                # Capture image
                result = await self.client.execute_command(
                    device_id=self.camera_device_id,
                    command='capture_image',
                    params={
                        'width': width,
                        'height': height,
                        'format': 'jpeg',
                        'quality': 90
                    }
                )
                
                if 'error' in result:
                    self.logger.error(f"Timelapse image {i+1}/{count} capture failed: {result['error']}")
                    continue
                
                # Save image
                if 'image_data' in result:
                    try:
                        # Decode base64 data if present
                        if isinstance(result['image_data'], str):
                            image_data = base64.b64decode(result['image_data'])
                        else:
                            image_data = result['image_data']
                            
                        # Save image file
                        with open(filename, 'wb') as f:
                            f.write(image_data)
                                
                        self.logger.info(f"Timelapse image {i+1}/{count} saved to {filename}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to save timelapse image: {e}")
                
                # Wait for the next interval (unless this is the last image)
                if i < count - 1:
                    await asyncio.sleep(interval)
            
            self.logger.info(f"Timelapse sequence completed: {count} images saved to {output_dir}")
            
            return {'status': 'success', 'count': count, 'output_dir': output_dir}
            
        except Exception as e:
            self.logger.error(f"Failed to capture timelapse: {e}")
            return {'error': str(e)}

    async def capture_with_effects(
            self,
            output_file: str = 'rpi_camera_effect.jpg',
            effect: str = 'negative',
            resolution: str = '1920x1080'
    ) -> Dict[str, Any]:
        """
        Capture an image with special effects from the Raspberry Pi Camera Module.

        Args:
            output_file: Path to save the image
            effect: Image effect to apply (negative, solarize, sketch, etc.)
            resolution: Image resolution (WxH)

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Capturing image with '{effect}' effect")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Execute capture command with effect
            result = await self.client.execute_command(
                device_id=self.camera_device_id,
                command='capture_image',
                params={
                    'width': width,
                    'height': height,
                    'format': 'jpeg',
                    'quality': 90,
                    'effect': effect
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Image capture with effect failed: {result['error']}")
                return result
                
            self.logger.info(f"Image with '{effect}' effect captured successfully")
            
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
            self.logger.error(f"Failed to capture image with effect: {e}")
            return {'error': str(e)}


async def main():
    """
    Run the Raspberry Pi Camera example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Camera Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--output', help='Output file or directory')
    parser.add_argument('--resolution', default='1920x1080', help='Image/video resolution (WxH)')
    parser.add_argument('--demo', choices=['image', 'video', 'timelapse', 'effect'], 
                        default='image', help='Demo to run')
    parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    parser.add_argument('--fps', type=int, default=30, help='Video frames per second')
    parser.add_argument('--interval', type=int, default=2, help='Timelapse interval in seconds')
    parser.add_argument('--count', type=int, default=10, help='Timelapse image count')
    parser.add_argument('--effect', default='negative', 
                        choices=['negative', 'solarize', 'sketch', 'denoise', 'emboss', 'oilpaint', 'hatch', 'gpen'],
                        help='Image effect to apply')
    
    args = parser.parse_args()
    
    example = RPiCameraExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover camera
    if not await example.discover_camera():
        print("Failed to discover Raspberry Pi Camera. Make sure the UnitAPI server is running and the camera is connected.")
        return
    
    # Run the selected demo
    if args.demo == 'image':
        output_file = args.output or 'rpi_camera_capture.jpg'
        await example.capture_image(output_file, args.resolution)
        
    elif args.demo == 'video':
        output_file = args.output or 'rpi_camera_video.mp4'
        await example.capture_video(output_file, args.duration, args.resolution, args.fps)
        
    elif args.demo == 'timelapse':
        output_dir = args.output or 'rpi_timelapse'
        await example.capture_timelapse(output_dir, args.interval, args.count, args.resolution)
        
    elif args.demo == 'effect':
        output_file = args.output or f'rpi_camera_{args.effect}.jpg'
        await example.capture_with_effects(output_file, args.effect, args.resolution)


if __name__ == "__main__":
    asyncio.run(main())
