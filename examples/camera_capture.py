#!/usr/bin/env python3
"""
Camera Capture Example

This script demonstrates how to capture images from local and remote cameras,
as well as take screenshots.
"""

import asyncio
import argparse
import logging
import base64
import os
from typing import Optional, Dict, Any, List

from unitapi.core.client import UnitAPIClient


class CameraCaptureExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize camera capture example.

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

    async def list_cameras(self) -> List[Dict[str, Any]]:
        """
        List available cameras.

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
                self.logger.info(f"Found {len(cameras)} camera(s)")
                for i, camera in enumerate(cameras):
                    camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
                    self.logger.info(f"Camera {i+1}: {camera.get('name')} ({camera_type}) (ID: {camera.get('device_id')})")
            else:
                self.logger.warning("No cameras found")
                
            return cameras
            
        except Exception as e:
            self.logger.error(f"Failed to list cameras: {e}")
            return []

    async def capture_from_device(
            self,
            device_id: str,
            output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Capture an image from a remote camera device.

        Args:
            device_id: Camera device ID
            output_file: Optional path to save the image

        Returns:
            Capture result
        """
        try:
            self.logger.info(f"Capturing image from device {device_id}...")
            
            # Execute capture command
            result = await self.client.execute_command(
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
            self.logger.error(f"Failed to capture from device: {e}")
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

    async def take_screenshot(
            self,
            output_file: str = 'screenshot.png'
    ) -> bool:
        """
        Take a screenshot of the current screen.

        Args:
            output_file: Path to save the screenshot

        Returns:
            Success status
        """
        try:
            # Try to use PyAutoGUI for screenshots
            import pyautogui
            
            self.logger.info("Taking screenshot...")
            screenshot = pyautogui.screenshot()
            
            # Save the screenshot
            screenshot.save(output_file)
            self.logger.info(f"Screenshot saved to {output_file}")
            
            return True
            
        except ImportError:
            # Try alternative methods
            try:
                # Try using PIL directly
                from PIL import ImageGrab
                
                self.logger.info("Taking screenshot with PIL...")
                screenshot = ImageGrab.grab()
                screenshot.save(output_file)
                self.logger.info(f"Screenshot saved to {output_file}")
                
                return True
                
            except ImportError:
                # Try platform-specific methods
                import platform
                system = platform.system()
                
                if system == 'Linux':
                    # Try using xlib
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with scrot...")
                        subprocess.run(['scrot', output_file], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with scrot: {e}")
                        return False
                        
                elif system == 'Windows':
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with Windows API...")
                        # PowerShell command to take screenshot
                        ps_cmd = (
                            "$wia = New-Object -ComObject WIA.CommonDialog; "
                            "$img = $wia.ShowAcquireImage(); "
                            "$img.SaveFile('" + output_file.replace('\\', '\\\\') + "')"
                        )
                        subprocess.run(['powershell', '-Command', ps_cmd], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with Windows API: {e}")
                        return False
                        
                elif system == 'Darwin':  # macOS
                    try:
                        import subprocess
                        self.logger.info("Taking screenshot with macOS screencapture...")
                        subprocess.run(['screencapture', output_file], check=True)
                        self.logger.info(f"Screenshot saved to {output_file}")
                        return True
                    except Exception as e:
                        self.logger.error(f"Failed to take screenshot with screencapture: {e}")
                        return False
                
                self.logger.error("No screenshot method available for this platform")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False


async def main():
    """
    Run the camera capture example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Camera Capture Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--local', action='store_true', help='Use local camera directly')
    parser.add_argument('--camera-index', type=int, default=0, help='Local camera index (0 for internal, 1+ for external)')
    parser.add_argument('--screenshot', action='store_true', help='Take a screenshot instead of camera capture')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--remote-device-id', help='Specific remote camera device ID to use')
    
    args = parser.parse_args()
    
    example = CameraCaptureExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    if args.screenshot:
        # Take a screenshot
        output_file = args.output or 'screenshot.png'
        await example.take_screenshot(output_file)
    elif args.local:
        # Capture from local camera
        output_file = args.output or f'camera_{args.camera_index}_capture.jpg'
        await example.capture_local_camera(
            camera_index=args.camera_index,
            output_file=output_file
        )
    else:
        # Use remote camera through UnitAPI
        if args.remote_device_id:
            # Use specified device ID
            device_id = args.remote_device_id
            output_file = args.output or f'camera_{device_id}_capture.jpg'
            await example.capture_from_device(
                device_id=device_id,
                output_file=output_file
            )
        else:
            # List available cameras and use the first one
            cameras = await example.list_cameras()
            
            if cameras:
                # Use the first camera
                camera = cameras[0]
                device_id = camera.get('device_id')
                camera_type = camera.get('metadata', {}).get('camera_type', 'unknown')
                
                output_file = args.output or f'camera_{camera_type}_capture.jpg'
                await example.capture_from_device(
                    device_id=device_id,
                    output_file=output_file
                )
            else:
                print("No cameras available. Run the device discovery service first.")


if __name__ == "__main__":
    asyncio.run(main())
