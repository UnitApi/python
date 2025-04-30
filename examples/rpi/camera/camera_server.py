#!/usr/bin/env python3
"""
Raspberry Pi Camera Server Example

This script demonstrates how to create a UnitAPI server that exposes the Raspberry Pi
Camera Module functionality. This server can be used with the camera_module.py client example.
"""

import asyncio
import argparse
import logging
import signal
import sys
import os
import base64
import time
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.devices.camera import CameraDevice


class RPiCameraServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Camera server.

        Args:
            host: Server host address
            port: Server port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI Server
        self.server = UnitAPIServer(host=host, port=port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(
            host=host,
            port=port + 1
        )
        
        # Camera Device
        self.camera_device = None
        
        # Active video recordings
        self.active_recordings = {}
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        self.logger.info("Shutdown signal received, cleaning up...")
        
        # Create a new event loop for cleanup
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run cleanup
            loop.run_until_complete(self._cleanup())
        finally:
            loop.close()
            sys.exit(0)

    async def _cleanup(self):
        """Clean up resources before shutdown."""
        if self.camera_device:
            try:
                # Stop any active recordings
                for recording_id in list(self.active_recordings.keys()):
                    try:
                        await self.stop_video_recording({'recording_id': recording_id})
                    except Exception as e:
                        self.logger.error(f"Error stopping recording {recording_id}: {e}")
                
                await self.camera_device.disconnect()
                self.logger.info("Camera device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting camera device: {e}")

    async def setup_camera_device(self):
        """
        Set up and register the camera device.

        Returns:
            Success status
        """
        try:
            # Check if Raspberry Pi camera is available
            camera_available = self._check_camera_available()
            
            if not camera_available:
                self.logger.warning("Raspberry Pi Camera not detected. Using virtual camera.")
            
            # Create camera device
            self.camera_device = CameraDevice(
                device_id="camera_rpi",
                name="Raspberry Pi Camera",
                metadata={
                    "camera_type": "raspberry_pi",
                    "virtual": not camera_available
                }
            )
            
            # Connect the device
            await self.camera_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.camera_device.device_id,
                device_type=self.camera_device.type,
                metadata=self.camera_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.camera_device.device_id,
                command="capture_image",
                handler=self.capture_image
            )
            
            self.server.register_command_handler(
                device_id=self.camera_device.device_id,
                command="start_video_recording",
                handler=self.start_video_recording
            )
            
            self.server.register_command_handler(
                device_id=self.camera_device.device_id,
                command="stop_video_recording",
                handler=self.stop_video_recording
            )
            
            self.logger.info(f"Camera device registered: {self.camera_device.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up camera device: {e}")
            return False

    def _check_camera_available(self) -> bool:
        """
        Check if Raspberry Pi camera is available.

        Returns:
            True if camera is available, False otherwise
        """
        try:
            # Method 1: Check for /dev/video0
            if os.path.exists('/dev/video0'):
                return True
                
            # Method 2: Try to import picamera
            try:
                import picamera
                return True
            except ImportError:
                pass
                
            # Method 3: Check vcgencmd get_camera output
            try:
                import subprocess
                result = subprocess.run(['vcgencmd', 'get_camera'], 
                                       capture_output=True, text=True, check=True)
                if 'detected=1' in result.stdout:
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking camera availability: {e}")
            return False

    async def capture_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture an image from the Raspberry Pi Camera.

        Args:
            params: Command parameters including width, height, format, quality, effect

        Returns:
            Capture result with image data
        """
        try:
            width = params.get('width', 1920)
            height = params.get('height', 1080)
            image_format = params.get('format', 'jpeg')
            quality = params.get('quality', 90)
            effect = params.get('effect', None)
            
            self.logger.info(f"Capturing {width}x{height} image in {image_format} format")
            
            # Check if we're using a virtual camera
            if self.camera_device.metadata.get('virtual', False):
                # Generate a test pattern image
                image_data = self._generate_test_image(width, height, effect)
            else:
                # Capture from real camera
                image_data = await self._capture_from_camera(width, height, image_format, quality, effect)
            
            # Encode image data as base64
            encoded_data = base64.b64encode(image_data).decode('utf-8')
            
            return {
                'width': width,
                'height': height,
                'format': image_format,
                'image_data': encoded_data,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Image capture failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _capture_from_camera(
            self, 
            width: int, 
            height: int, 
            image_format: str,
            quality: int,
            effect: Optional[str]
    ) -> bytes:
        """
        Capture an image from the physical Raspberry Pi Camera.

        Args:
            width: Image width
            height: Image height
            image_format: Image format (jpeg, png)
            quality: Image quality (0-100)
            effect: Image effect to apply

        Returns:
            Raw image data
        """
        # Try to use picamera if available
        try:
            import picamera
            import io
            
            stream = io.BytesIO()
            
            with picamera.PiCamera() as camera:
                # Set resolution
                camera.resolution = (width, height)
                
                # Apply effect if specified
                if effect:
                    camera.image_effect = effect
                
                # Warm up camera
                camera.start_preview()
                await asyncio.sleep(0.5)  # Allow camera to adjust
                
                # Capture to stream
                if image_format.lower() == 'jpeg':
                    camera.capture(stream, format='jpeg', quality=quality)
                else:
                    camera.capture(stream, format=image_format)
                
                # Get image data
                stream.seek(0)
                return stream.getvalue()
                
        except ImportError:
            # Fall back to OpenCV if picamera is not available
            try:
                import cv2
                import numpy as np
                
                # Open camera
                cap = cv2.VideoCapture(0)
                
                # Set resolution
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                # Capture frame
                ret, frame = cap.read()
                
                # Release camera
                cap.release()
                
                if not ret:
                    raise Exception("Failed to capture frame")
                
                # Apply effect if specified
                if effect:
                    if effect == 'negative':
                        frame = cv2.bitwise_not(frame)
                    elif effect == 'grayscale':
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    elif effect == 'sketch':
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        blur = cv2.GaussianBlur(gray, (5, 5), 0)
                        edges = cv2.Canny(blur, 50, 150)
                        ret, mask = cv2.threshold(edges, 70, 255, cv2.THRESH_BINARY_INV)
                        frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                
                # Encode image
                if image_format.lower() == 'jpeg':
                    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                    _, buffer = cv2.imencode('.jpg', frame, encode_params)
                elif image_format.lower() == 'png':
                    _, buffer = cv2.imencode('.png', frame)
                else:
                    _, buffer = cv2.imencode('.jpg', frame)
                
                return buffer.tobytes()
                
            except Exception as e:
                self.logger.error(f"OpenCV capture failed: {e}")
                # Fall back to test pattern
                return self._generate_test_image(width, height, effect)

    def _generate_test_image(
            self, 
            width: int, 
            height: int, 
            effect: Optional[str] = None
    ) -> bytes:
        """
        Generate a test pattern image when no camera is available.

        Args:
            width: Image width
            height: Image height
            effect: Image effect to apply

        Returns:
            Raw image data
        """
        try:
            import numpy as np
            import cv2
            
            # Create a test pattern (color bars)
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Divide width into 8 segments
            segment_width = width // 8
            
            # Define colors for test pattern
            colors = [
                (255, 255, 255),  # White
                (255, 255, 0),    # Yellow
                (0, 255, 255),    # Cyan
                (0, 255, 0),      # Green
                (255, 0, 255),    # Magenta
                (255, 0, 0),      # Red
                (0, 0, 255),      # Blue
                (0, 0, 0)         # Black
            ]
            
            # Draw color bars
            for i, color in enumerate(colors):
                start_x = i * segment_width
                end_x = (i + 1) * segment_width if i < 7 else width
                img[:, start_x:end_x] = color
            
            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, 'Raspberry Pi', (width//4, height//2), 
                       font, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, 'Test Pattern', (width//4, height//2 + 40), 
                       font, 1, (0, 0, 0), 2, cv2.LINE_AA)
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(img, timestamp, (10, height - 10), 
                       font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            
            # Apply effect if specified
            if effect:
                if effect == 'negative':
                    img = cv2.bitwise_not(img)
                elif effect == 'grayscale':
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                elif effect == 'sketch':
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    edges = cv2.Canny(blur, 50, 150)
                    ret, mask = cv2.threshold(edges, 70, 255, cv2.THRESH_BINARY_INV)
                    img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            return buffer.tobytes()
            
        except Exception as e:
            self.logger.error(f"Failed to generate test image: {e}")
            
            # Return a minimal image if all else fails
            return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00\xff\xd9'

    async def start_video_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start video recording from the Raspberry Pi Camera.

        Args:
            params: Command parameters including width, height, fps, format, output_file

        Returns:
            Recording start result with recording ID
        """
        try:
            width = params.get('width', 1280)
            height = params.get('height', 720)
            fps = params.get('fps', 30)
            video_format = params.get('format', 'h264')
            output_file = params.get('output_file', f'rpi_video_{int(time.time())}.mp4')
            
            self.logger.info(f"Starting {width}x{height} video recording at {fps} fps")
            
            # Generate unique recording ID
            recording_id = f"rec_{int(time.time())}_{len(self.active_recordings)}"
            
            # Check if we're using a virtual camera
            if self.camera_device.metadata.get('virtual', False):
                # Simulate recording for virtual camera
                self.active_recordings[recording_id] = {
                    'start_time': time.time(),
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'format': video_format,
                    'output_file': output_file,
                    'virtual': True
                }
                
                self.logger.info(f"Started virtual video recording (ID: {recording_id})")
            else:
                # Start actual recording
                recording_process = await self._start_camera_recording(
                    width, height, fps, video_format, output_file
                )
                
                self.active_recordings[recording_id] = {
                    'start_time': time.time(),
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'format': video_format,
                    'output_file': output_file,
                    'process': recording_process,
                    'virtual': False
                }
                
                self.logger.info(f"Started video recording (ID: {recording_id})")
            
            return {
                'recording_id': recording_id,
                'start_time': self.active_recordings[recording_id]['start_time'],
                'output_file': output_file,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Video recording start failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _start_camera_recording(
            self,
            width: int,
            height: int,
            fps: int,
            video_format: str,
            output_file: str
    ) -> Any:
        """
        Start actual video recording from the physical Raspberry Pi Camera.

        Args:
            width: Video width
            height: Video height
            fps: Frames per second
            video_format: Video format (h264, mp4)
            output_file: Output file path

        Returns:
            Recording process or object
        """
        # Try to use picamera if available
        try:
            import picamera
            import subprocess
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Start recording using raspivid command for better performance
            cmd = [
                'raspivid',
                '-o', output_file,
                '-w', str(width),
                '-h', str(height),
                '-fps', str(fps),
                '-t', '0'  # Record until stopped
            ]
            
            # Start the process
            process = subprocess.Popen(cmd)
            return process
                
        except (ImportError, FileNotFoundError):
            # Fall back to OpenCV if picamera is not available
            try:
                import cv2
                import threading
                
                # Create video writer
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
                
                # Create stop event
                stop_event = threading.Event()
                
                # Recording thread function
                def record_thread():
                    cap = cv2.VideoCapture(0)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    
                    while not stop_event.is_set():
                        ret, frame = cap.read()
                        if ret:
                            out.write(frame)
                        else:
                            break
                    
                    cap.release()
                    out.release()
                
                # Start recording thread
                thread = threading.Thread(target=record_thread)
                thread.start()
                
                return {
                    'thread': thread,
                    'stop_event': stop_event,
                    'output': out
                }
                
            except Exception as e:
                self.logger.error(f"OpenCV recording failed: {e}")
                # Return None for virtual recording
                return None

    async def stop_video_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop video recording.

        Args:
            params: Command parameters including recording_id

        Returns:
            Recording stop result
        """
        try:
            recording_id = params.get('recording_id')
            
            if not recording_id or recording_id not in self.active_recordings:
                return {'error': 'Invalid recording ID', 'status': 'error'}
            
            recording = self.active_recordings[recording_id]
            duration = time.time() - recording['start_time']
            
            # Stop the recording
            if recording.get('virtual', True):
                # For virtual recording, just remove from active recordings
                pass
            else:
                # Stop actual recording
                await self._stop_camera_recording(recording)
            
            # Remove from active recordings
            del self.active_recordings[recording_id]
            
            self.logger.info(f"Stopped video recording (ID: {recording_id}, duration: {duration:.2f}s)")
            
            return {
                'recording_id': recording_id,
                'duration': duration,
                'output_file': recording['output_file'],
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Video recording stop failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _stop_camera_recording(self, recording: Dict[str, Any]) -> None:
        """
        Stop actual video recording.

        Args:
            recording: Recording information
        """
        try:
            if 'process' in recording:
                # Stop raspivid process
                process = recording['process']
                process.terminate()
                try:
                    process.wait(timeout=5)
                except:
                    process.kill()
            elif 'thread' in recording:
                # Stop OpenCV recording thread
                recording['stop_event'].set()
                recording['thread'].join(timeout=5)
                
                # Close output if still open
                if 'output' in recording and recording['output']:
                    try:
                        recording['output'].release()
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")

    async def start(self):
        """
        Start the camera server.
        """
        try:
            # Set up camera device
            if not await self.setup_camera_device():
                self.logger.error("Failed to set up camera device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi Camera Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi Camera server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Camera Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    server = RPiCameraServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
