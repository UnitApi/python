#!/usr/bin/env python3
"""
Camera Frame Capture Example

This script demonstrates how to capture a single frame from an internal or external camera.
"""

import asyncio
import argparse
import logging
import os
from datetime import datetime
import cv2
import numpy as np


class CameraFrameCaptureExample:
    def __init__(self, debug: bool = False):
        """
        Initialize camera frame capture example.

        Args:
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    async def list_cameras(self):
        """
        List available cameras on the system.
        
        Returns:
            List of available camera indices and their information
        """
        available_cameras = []
        
        # Check for video devices in /dev (Linux)
        try:
            import glob
            if os.path.exists('/dev'):
                video_devices = glob.glob('/dev/video*')
                for device_path in video_devices:
                    try:
                        device_num = int(device_path.replace('/dev/video', ''))
                        camera_type = "internal" if device_num == 0 else "external"
                        available_cameras.append({
                            'index': device_num,
                            'path': device_path,
                            'type': camera_type
                        })
                        self.logger.info(f"Found camera at {device_path} (index: {device_num}, type: {camera_type})")
                    except Exception as e:
                        self.logger.debug(f"Error processing video device {device_path}: {e}")
        except Exception as e:
            self.logger.debug(f"Error checking system devices: {e}")
        
        # Try to open cameras using OpenCV
        if not available_cameras:
            for i in range(5):  # Check first 5 potential camera indices
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        # Get camera properties
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        
                        # Release the camera
                        cap.release()
                        
                        camera_type = "internal" if i == 0 else "external"
                        available_cameras.append({
                            'index': i,
                            'resolution': f"{width}x{height}",
                            'fps': fps,
                            'type': camera_type
                        })
                        
                        self.logger.info(f"Found camera at index {i} ({width}x{height}, {fps} fps, type: {camera_type})")
                except Exception as e:
                    self.logger.debug(f"No camera at index {i}: {e}")
        
        # If no cameras found, create a virtual camera entry
        if not available_cameras:
            self.logger.warning("No physical cameras detected, will use a virtual test pattern")
            available_cameras.append({
                'index': 0,
                'type': 'virtual',
                'resolution': '640x480'
            })
        
        return available_cameras

    async def capture_frame(self, camera_index: int = 0, output_file: str = None) -> bool:
        """
        Capture a single frame from a camera.

        Args:
            camera_index: Camera device index (0 for internal, 1+ for external)
            output_file: Path to save the captured frame. If None, a timestamped filename will be used.

        Returns:
            Success status
        """
        # Generate default filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"camera_{camera_index}_{timestamp}.jpg"
        
        try:
            self.logger.info(f"Opening camera {camera_index}...")
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                self.logger.error(f"Failed to open camera {camera_index}")
                
                # If it's a virtual camera, generate a test pattern
                if camera_index == 0:
                    self.logger.info("Generating virtual camera test pattern")
                    # Create a test pattern image (color bars)
                    height, width = 480, 640
                    img = np.zeros((height, width, 3), dtype=np.uint8)
                    
                    # Create color bars
                    bar_width = width // 7
                    colors = [
                        (255, 255, 255),  # White
                        (255, 255, 0),    # Yellow
                        (0, 255, 255),    # Cyan
                        (0, 255, 0),      # Green
                        (255, 0, 255),    # Magenta
                        (255, 0, 0),      # Red
                        (0, 0, 255)       # Blue
                    ]
                    
                    for i, color in enumerate(colors):
                        img[:, i*bar_width:(i+1)*bar_width] = color
                    
                    # Add text
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img, "Virtual Camera", (width//2-100, height//2), 
                                font, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(img, timestamp_str, (width//2-100, height//2+40), 
                                font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
                    
                    # Save the image
                    cv2.imwrite(output_file, img)
                    self.logger.info(f"Virtual camera test pattern saved to {output_file}")
                    return True
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
            
            # Add timestamp to the image
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, timestamp_str, (10, height-20), 
                        font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Save the image
            cv2.imwrite(output_file, frame)
            self.logger.info(f"Frame saved to {output_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to capture from camera: {e}")
            return False


async def main():
    """
    Run the camera frame capture example.
    """
    parser = argparse.ArgumentParser(description='Camera Frame Capture Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--list', action='store_true', help='List available cameras')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (0 for internal, 1+ for external)')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    example = CameraFrameCaptureExample(debug=args.debug)
    
    if args.list:
        # List available cameras
        await example.list_cameras()
    else:
        # Capture frame from camera
        await example.capture_frame(camera_index=args.camera, output_file=args.output)


if __name__ == "__main__":
    asyncio.run(main())
