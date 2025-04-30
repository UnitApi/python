#!/usr/bin/env python3
"""
Raspberry Pi ReSpeaker Server Example

This script demonstrates how to create a UnitAPI server that exposes ReSpeaker microphone array
functionality on a Raspberry Pi. This server can be used with the respeaker_client.py client example.
"""

import asyncio
import argparse
import logging
import signal
import sys
import os
import time
import base64
from typing import Dict, Any, List, Optional

from unitapi.core.server import UnitAPIServer
from unitapi.protocols.websocket import WebSocketProtocol


class RPiReSpeakerServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi ReSpeaker server.

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
        
        # ReSpeaker Device
        self.respeaker_device = None
        
        # Active recordings
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
        if self.respeaker_device:
            try:
                # Stop any active recordings
                for recording_id in list(self.active_recordings.keys()):
                    try:
                        await self.stop_recording({'recording_id': recording_id})
                    except Exception as e:
                        self.logger.error(f"Error stopping recording {recording_id}: {e}")
                
                await self.respeaker_device.disconnect()
                self.logger.info("ReSpeaker device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting ReSpeaker device: {e}")

    async def setup_respeaker_device(self):
        """
        Set up and register the ReSpeaker device.

        Returns:
            Success status
        """
        try:
            # Check if ReSpeaker is available
            respeaker_available = self._check_respeaker_available()
            
            if not respeaker_available:
                self.logger.warning("ReSpeaker not detected. Using virtual ReSpeaker.")
            
            # Create ReSpeaker device
            from unitapi.devices.base import BaseDevice, DeviceStatus
            
            class ReSpeakerDevice(BaseDevice):
                """ReSpeaker device implementation."""
                
                def __init__(self, device_id: str, name: str, metadata: Dict[str, Any] = None):
                    """Initialize ReSpeaker device."""
                    super().__init__(
                        device_id=device_id,
                        name=name,
                        device_type="microphone",
                        metadata=metadata or {}
                    )
                    self.logger = logging.getLogger(__name__)
                    self.status = DeviceStatus.OFFLINE
                
                async def connect(self) -> bool:
                    """Connect to the ReSpeaker device."""
                    try:
                        # Simulated connection logic
                        await asyncio.sleep(0.5)
                        self.status = DeviceStatus.ONLINE
                        self.logger.info(f"ReSpeaker Device {self.device_id} connected")
                        return True
                    except Exception as e:
                        self.status = DeviceStatus.ERROR
                        self.logger.error(f"ReSpeaker Device connection failed: {e}")
                        return False
                
                async def disconnect(self) -> bool:
                    """Disconnect from the ReSpeaker device."""
                    try:
                        # Simulated disconnection logic
                        await asyncio.sleep(0.5)
                        self.status = DeviceStatus.OFFLINE
                        self.logger.info(f"ReSpeaker Device {self.device_id} disconnected")
                        return True
                    except Exception as e:
                        self.logger.error(f"ReSpeaker Device disconnection failed: {e}")
                        return False
            
            # Create ReSpeaker device instance
            self.respeaker_device = ReSpeakerDevice(
                device_id="respeaker_rpi",
                name="Raspberry Pi ReSpeaker",
                metadata={
                    "microphone_type": "respeaker",
                    "virtual": not respeaker_available,
                    "sample_rate": 16000,
                    "channels": 4,
                    "model": "ReSpeaker 4-Mic Array"
                }
            )
            
            # Connect the device
            await self.respeaker_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.respeaker_device.device_id,
                device_type=self.respeaker_device.type,
                metadata=self.respeaker_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.respeaker_device.device_id,
                command="start_recording",
                handler=self.start_recording
            )
            
            self.server.register_command_handler(
                device_id=self.respeaker_device.device_id,
                command="stop_recording",
                handler=self.stop_recording
            )
            
            self.server.register_command_handler(
                device_id=self.respeaker_device.device_id,
                command="get_audio_level",
                handler=self.get_audio_level
            )
            
            self.server.register_command_handler(
                device_id=self.respeaker_device.device_id,
                command="get_direction",
                handler=self.get_direction
            )
            
            self.server.register_command_handler(
                device_id=self.respeaker_device.device_id,
                command="set_led_pattern",
                handler=self.set_led_pattern
            )
            
            self.logger.info(f"ReSpeaker device registered: {self.respeaker_device.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up ReSpeaker device: {e}")
            return False

    def _check_respeaker_available(self) -> bool:
        """
        Check if a ReSpeaker microphone array is available.

        Returns:
            True if ReSpeaker is available, False otherwise
        """
        try:
            # Try to detect ReSpeaker hardware
            import subprocess
            
            # Check for ReSpeaker USB device
            cmd = ['lsusb']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if 'ReSpeaker' in result.stdout or '2886:0018' in result.stdout:
                return True
            
            # Check for ReSpeaker kernel modules
            cmd = ['lsmod']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if 'snd_soc_seeed_voicecard' in result.stdout:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking ReSpeaker availability: {e}")
            return False

    async def start_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start audio recording from the ReSpeaker.

        Args:
            params: Command parameters including sample_rate, channels, format, output_file

        Returns:
            Recording start result with recording ID
        """
        try:
            sample_rate = params.get('sample_rate', 16000)
            channels = params.get('channels', 1)  # Default to 1 channel (beamformed)
            audio_format = params.get('format', 'wav')
            output_file = params.get('output_file', f'respeaker_audio_{int(time.time())}.{audio_format}')
            duration = params.get('duration', None)  # None for unlimited
            
            self.logger.info(f"Starting ReSpeaker recording at {sample_rate}Hz with {channels} channel(s)")
            
            # Generate unique recording ID
            recording_id = f"rec_{int(time.time())}_{len(self.active_recordings)}"
            
            # Check if we're using a virtual ReSpeaker
            if self.respeaker_device.metadata.get('virtual', False):
                # Simulate recording for virtual ReSpeaker
                self.active_recordings[recording_id] = {
                    'start_time': time.time(),
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'format': audio_format,
                    'output_file': output_file,
                    'duration': duration,
                    'virtual': True
                }
                
                self.logger.info(f"Started virtual ReSpeaker recording (ID: {recording_id})")
                
                # If duration is specified, schedule stop
                if duration is not None:
                    asyncio.create_task(self._auto_stop_recording(recording_id, duration))
            else:
                # Start actual recording
                recording_process = await self._start_respeaker_recording(
                    sample_rate, channels, audio_format, output_file
                )
                
                self.active_recordings[recording_id] = {
                    'start_time': time.time(),
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'format': audio_format,
                    'output_file': output_file,
                    'duration': duration,
                    'process': recording_process,
                    'virtual': False
                }
                
                self.logger.info(f"Started ReSpeaker recording (ID: {recording_id})")
                
                # If duration is specified, schedule stop
                if duration is not None:
                    asyncio.create_task(self._auto_stop_recording(recording_id, duration))
            
            return {
                'recording_id': recording_id,
                'start_time': self.active_recordings[recording_id]['start_time'],
                'output_file': output_file,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"ReSpeaker recording start failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _auto_stop_recording(self, recording_id: str, duration: float):
        """
        Automatically stop recording after specified duration.

        Args:
            recording_id: Recording ID
            duration: Recording duration in seconds
        """
        try:
            await asyncio.sleep(duration)
            
            # Check if recording is still active
            if recording_id in self.active_recordings:
                self.logger.info(f"Auto-stopping recording {recording_id} after {duration}s")
                await self.stop_recording({'recording_id': recording_id})
        except Exception as e:
            self.logger.error(f"Error in auto-stop recording: {e}")

    async def _start_respeaker_recording(
            self,
            sample_rate: int,
            channels: int,
            audio_format: str,
            output_file: str
    ) -> Any:
        """
        Start actual audio recording from the ReSpeaker.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            audio_format: Audio format (wav, mp3)
            output_file: Output file path

        Returns:
            Recording process or object
        """
        try:
            import subprocess
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Use arecord for ReSpeaker recording
            cmd = [
                'arecord',
                '-D', 'plughw:seeed-4mic,0',  # ReSpeaker device
                '-f', 'S16_LE',
                '-c', str(channels),
                '-r', str(sample_rate),
                '-t', 'wav',
                '-d', '0'  # Record until stopped
            ]
            
            if audio_format.lower() == 'wav':
                # Direct WAV output
                cmd.append(output_file)
                
                # Start the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                return process
            else:
                # Pipe to ffmpeg for other formats
                cmd.append('-')  # Output to stdout
                
                # Start arecord process
                arecord_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Set up ffmpeg command
                if audio_format.lower() == 'mp3':
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-i', 'pipe:0',
                        '-f', 'mp3',
                        '-acodec', 'libmp3lame',
                        '-ab', '192k',
                        output_file
                    ]
                else:
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-i', 'pipe:0',
                        '-f', audio_format,
                        output_file
                    ]
                
                # Start ffmpeg process
                ffmpeg_process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdin=arecord_process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Allow arecord to receive SIGPIPE if ffmpeg exits
                arecord_process.stdout.close()
                
                return {
                    'arecord': arecord_process,
                    'ffmpeg': ffmpeg_process
                }
                
        except Exception as e:
            self.logger.error(f"Failed to start ReSpeaker recording: {e}")
            return None

    async def stop_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop audio recording.

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
                # For virtual recording, generate a test audio file
                if recording['format'].lower() == 'wav':
                    await self._generate_test_audio(
                        recording['output_file'],
                        recording['sample_rate'],
                        recording['channels'],
                        duration
                    )
            else:
                # Stop actual recording
                await self._stop_respeaker_recording(recording)
            
            # Remove from active recordings
            del self.active_recordings[recording_id]
            
            self.logger.info(f"Stopped ReSpeaker recording (ID: {recording_id}, duration: {duration:.2f}s)")
            
            return {
                'recording_id': recording_id,
                'duration': duration,
                'output_file': recording['output_file'],
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"ReSpeaker recording stop failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _stop_respeaker_recording(self, recording: Dict[str, Any]) -> None:
        """
        Stop actual audio recording.

        Args:
            recording: Recording information
        """
        try:
            if 'process' in recording and recording['process']:
                # Simple process
                process = recording['process']
                
                # Terminate the process
                process.terminate()
                
                try:
                    process.wait(timeout=5)
                except:
                    # Force kill if termination times out
                    process.kill()
                    
            elif 'arecord' in recording or 'ffmpeg' in recording:
                # Stop arecord and ffmpeg processes
                if 'arecord' in recording and recording['arecord']:
                    try:
                        recording['arecord'].terminate()
                        recording['arecord'].wait(timeout=5)
                    except:
                        recording['arecord'].kill()
                
                if 'ffmpeg' in recording and recording['ffmpeg']:
                    try:
                        recording['ffmpeg'].terminate()
                        recording['ffmpeg'].wait(timeout=5)
                    except:
                        recording['ffmpeg'].kill()
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")

    async def _generate_test_audio(
            self,
            output_file: str,
            sample_rate: int,
            channels: int,
            duration: float
    ) -> None:
        """
        Generate a test audio file for virtual ReSpeaker.

        Args:
            output_file: Output file path
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            duration: Audio duration in seconds
        """
        try:
            import numpy as np
            import wave
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Generate a sine wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz tone
            
            # Convert to 16-bit PCM
            audio = (tone * 32767).astype(np.int16)
            
            # Duplicate for multi-channel if needed
            if channels > 1:
                audio = np.column_stack([audio] * channels)
            
            # Write to WAV file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
                
            self.logger.info(f"Generated test audio file: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate test audio: {e}")

    async def get_audio_level(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current audio input level from each microphone.

        Args:
            params: Command parameters

        Returns:
            Audio level result
        """
        try:
            # Check if we're using a virtual ReSpeaker
            if self.respeaker_device.metadata.get('virtual', False):
                # Generate random audio levels for virtual ReSpeaker
                import random
                
                # Get number of channels
                channels = self.respeaker_device.metadata.get('channels', 4)
                
                # Generate levels for each channel
                levels = [random.uniform(0.0, 1.0) for _ in range(channels)]
                
                # Calculate average level
                avg_level = sum(levels) / len(levels)
                
                self.logger.debug(f"Virtual ReSpeaker audio levels: {levels}, avg: {avg_level:.2f}")
                
                return {
                    'levels': levels,
                    'average_level': avg_level,
                    'status': 'success'
                }
            else:
                # Get actual audio levels from ReSpeaker
                levels = await self._get_respeaker_levels()
                
                # Calculate average level
                avg_level = sum(levels) / len(levels)
                
                self.logger.debug(f"ReSpeaker audio levels: {levels}, avg: {avg_level:.2f}")
                
                return {
                    'levels': levels,
                    'average_level': avg_level,
                    'status': 'success'
                }
                
        except Exception as e:
            self.logger.error(f"Get audio level failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _get_respeaker_levels(self) -> List[float]:
        """
        Get actual audio levels from ReSpeaker.

        Returns:
            List of audio levels (0.0 to 1.0) for each channel
        """
        try:
            import pyaudio
            import numpy as np
            
            # PyAudio setup
            p = pyaudio.PyAudio()
            
            # Find ReSpeaker device
            device_index = None
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if 'seeed' in device_info.get('name', '').lower():
                    device_index = i
                    break
            
            if device_index is None:
                # Fall back to default input device
                device_index = p.get_default_input_device_info().get('index')
            
            # Get number of channels
            channels = self.respeaker_device.metadata.get('channels', 4)
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Read audio data
            data = stream.read(1024, exception_on_overflow=False)
            
            # Close stream
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Convert to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Reshape to separate channels
            audio_data = audio_data.reshape(-1, channels)
            
            # Calculate RMS level for each channel
            levels = []
            for channel in range(channels):
                channel_data = audio_data[:, channel]
                rms = np.sqrt(np.mean(np.square(channel_data)))
                
                # Normalize to 0.0-1.0 range (assuming 16-bit audio)
                level = min(1.0, rms / 32767)
                levels.append(level)
            
            return levels
            
        except Exception as e:
            self.logger.error(f"Failed to get ReSpeaker levels: {e}")
            
            # Return random levels as fallback
            import random
            channels = self.respeaker_device.metadata.get('channels', 4)
            return [random.uniform(0.0, 1.0) for _ in range(channels)]

    async def get_direction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the direction of sound (DOA - Direction of Arrival).

        Args:
            params: Command parameters

        Returns:
            Direction result
        """
        try:
            # Check if we're using a virtual ReSpeaker
            if self.respeaker_device.metadata.get('virtual', False):
                # Generate random direction for virtual ReSpeaker
                import random
                
                # Random angle (0-359 degrees)
                angle = random.randint(0, 359)
                
                self.logger.debug(f"Virtual ReSpeaker direction: {angle}°")
                
                return {
                    'angle': angle,
                    'status': 'success'
                }
            else:
                # Get actual direction from ReSpeaker
                angle = await self._get_respeaker_direction()
                
                self.logger.debug(f"ReSpeaker direction: {angle}°")
                
                return {
                    'angle': angle,
                    'status': 'success'
                }
                
        except Exception as e:
            self.logger.error(f"Get direction failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _get_respeaker_direction(self) -> int:
        """
        Get actual direction from ReSpeaker.

        Returns:
            Direction angle in degrees (0-359)
        """
        try:
            # This would normally use the ReSpeaker's DOA algorithm
            # For demonstration, we'll return a random angle
            import random
            return random.randint(0, 359)
            
        except Exception as e:
            self.logger.error(f"Failed to get ReSpeaker direction: {e}")
            
            # Return random direction as fallback
            import random
            return random.randint(0, 359)

    async def set_led_pattern(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the LED pattern on the ReSpeaker.

        Args:
            params: Command parameters including pattern, brightness, color

        Returns:
            LED pattern result
        """
        try:
            pattern = params.get('pattern', 'solid')
            brightness = params.get('brightness', 1.0)
            color = params.get('color', [0, 0, 255])  # Default blue
            
            self.logger.info(f"Setting ReSpeaker LED pattern: {pattern}, brightness: {brightness}, color: {color}")
            
            # Check if we're using a virtual ReSpeaker
            if self.respeaker_device.metadata.get('virtual', False):
                # Simulate LED pattern for virtual ReSpeaker
                self.logger.info(f"Virtual ReSpeaker LED pattern set: {pattern}")
                
                return {
                    'pattern': pattern,
                    'brightness': brightness,
                    'color': color,
                    'status': 'success'
                }
            else:
                # Set actual LED pattern on ReSpeaker
                await self._set_respeaker_leds(pattern, brightness, color)
                
                self.logger.info(f"ReSpeaker LED pattern set: {pattern}")
                
                return {
                    'pattern': pattern,
                    'brightness': brightness,
                    'color': color,
                    'status': 'success'
                }
                
        except Exception as e:
            self.logger.error(f"Set LED pattern failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _set_respeaker_leds(
            self,
            pattern: str,
            brightness: float,
            color: List[int]
    ) -> None:
        """
        Set actual LED pattern on ReSpeaker.

        Args:
            pattern: LED pattern ('solid', 'pulse', 'spin', 'custom')
            brightness: LED brightness (0.0 to 1.0)
            color: RGB color as [r, g, b] (0-255)
        """
        try:
            # This would normally use the ReSpeaker's LED control library
            # For demonstration, we'll just log the settings
            self.logger.info(f"Would set ReSpeaker LEDs to pattern={pattern}, brightness={brightness}, color={color}")
            
        except Exception as e:
            self.logger.error(f"Failed to set ReSpeaker LEDs: {e}")

    async def start(self):
        """
        Start the ReSpeaker server.
        """
        try:
            # Set up ReSpeaker device
            if not await self.setup_respeaker_device():
                self.logger.error("Failed to set up ReSpeaker device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi ReSpeaker Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi ReSpeaker server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi ReSpeaker Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    server = RPiReSpeakerServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
