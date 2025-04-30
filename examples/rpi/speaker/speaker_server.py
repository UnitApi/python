#!/usr/bin/env python3
"""
Raspberry Pi Speaker Server Example

This script demonstrates how to create a UnitAPI server that exposes speaker functionality
on a Raspberry Pi. This server can be used with the speaker_client.py client example.
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


class RPiSpeakerServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Speaker server.

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
        
        # Speaker Device
        self.speaker_device = None
        
        # Active playbacks
        self.active_playbacks = {}
        
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
        if self.speaker_device:
            try:
                # Stop any active playbacks
                for playback_id in list(self.active_playbacks.keys()):
                    try:
                        await self.stop_playback({'playback_id': playback_id})
                    except Exception as e:
                        self.logger.error(f"Error stopping playback {playback_id}: {e}")
                
                await self.speaker_device.disconnect()
                self.logger.info("Speaker device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting speaker device: {e}")

    async def setup_speaker_device(self):
        """
        Set up and register the speaker device.

        Returns:
            Success status
        """
        try:
            # Check if speaker is available
            speaker_available = self._check_speaker_available()
            
            if not speaker_available:
                self.logger.warning("No speaker detected. Using virtual speaker.")
            
            # Create speaker device
            from unitapi.devices.base import BaseDevice, DeviceStatus
            
            class SpeakerDevice(BaseDevice):
                """Speaker device implementation."""
                
                def __init__(self, device_id: str, name: str, metadata: Dict[str, Any] = None):
                    """Initialize speaker device."""
                    super().__init__(
                        device_id=device_id,
                        name=name,
                        device_type="speaker",
                        metadata=metadata or {}
                    )
                    self.logger = logging.getLogger(__name__)
                    self.status = DeviceStatus.OFFLINE
                
                async def connect(self) -> bool:
                    """Connect to the speaker device."""
                    try:
                        # Simulated connection logic
                        await asyncio.sleep(0.5)
                        self.status = DeviceStatus.ONLINE
                        self.logger.info(f"Speaker Device {self.device_id} connected")
                        return True
                    except Exception as e:
                        self.status = DeviceStatus.ERROR
                        self.logger.error(f"Speaker Device connection failed: {e}")
                        return False
                
                async def disconnect(self) -> bool:
                    """Disconnect from the speaker device."""
                    try:
                        # Simulated disconnection logic
                        await asyncio.sleep(0.5)
                        self.status = DeviceStatus.OFFLINE
                        self.logger.info(f"Speaker Device {self.device_id} disconnected")
                        return True
                    except Exception as e:
                        self.logger.error(f"Speaker Device disconnection failed: {e}")
                        return False
            
            # Create speaker device instance
            self.speaker_device = SpeakerDevice(
                device_id="speaker_rpi",
                name="Raspberry Pi Speaker",
                metadata={
                    "speaker_type": "raspberry_pi",
                    "virtual": not speaker_available,
                    "sample_rate": 44100,
                    "channels": 2
                }
            )
            
            # Connect the device
            await self.speaker_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.speaker_device.device_id,
                device_type=self.speaker_device.type,
                metadata=self.speaker_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.speaker_device.device_id,
                command="play_audio",
                handler=self.play_audio
            )
            
            self.server.register_command_handler(
                device_id=self.speaker_device.device_id,
                command="stop_playback",
                handler=self.stop_playback
            )
            
            self.server.register_command_handler(
                device_id=self.speaker_device.device_id,
                command="set_volume",
                handler=self.set_volume
            )
            
            self.server.register_command_handler(
                device_id=self.speaker_device.device_id,
                command="get_volume",
                handler=self.get_volume
            )
            
            self.logger.info(f"Speaker device registered: {self.speaker_device.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up speaker device: {e}")
            return False

    def _check_speaker_available(self) -> bool:
        """
        Check if a speaker is available.

        Returns:
            True if speaker is available, False otherwise
        """
        try:
            # Try to use PyAudio to detect speakers
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Check if any output devices are available
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                if device_info.get('maxOutputChannels') > 0:
                    p.terminate()
                    return True
            
            p.terminate()
            return False
            
        except ImportError:
            self.logger.warning("PyAudio not available for speaker detection")
            return False
        except Exception as e:
            self.logger.error(f"Error checking speaker availability: {e}")
            return False

    async def play_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Play audio through the speaker.

        Args:
            params: Command parameters including audio_file or audio_data

        Returns:
            Playback result with playback ID
        """
        try:
            audio_file = params.get('audio_file')
            audio_data_b64 = params.get('audio_data')
            loop = params.get('loop', False)
            volume = params.get('volume', 1.0)
            
            if not audio_file and not audio_data_b64:
                return {'error': 'Either audio_file or audio_data must be provided', 'status': 'error'}
            
            # Generate unique playback ID
            playback_id = f"play_{int(time.time())}_{len(self.active_playbacks)}"
            
            # Handle audio data if provided
            if audio_data_b64 and not audio_file:
                # Decode base64 audio data
                audio_data = base64.b64decode(audio_data_b64)
                
                # Save to temporary file
                audio_file = f"/tmp/rpi_audio_{playback_id}.wav"
                
                with open(audio_file, 'wb') as f:
                    f.write(audio_data)
                
                self.logger.info(f"Saved audio data to temporary file: {audio_file}")
            
            self.logger.info(f"Playing audio file: {audio_file}")
            
            # Start playback
            playback_process = await self._start_audio_playback(audio_file, volume, loop)
            
            # Store playback information
            self.active_playbacks[playback_id] = {
                'start_time': time.time(),
                'audio_file': audio_file,
                'loop': loop,
                'volume': volume,
                'process': playback_process,
                'temp_file': audio_data_b64 is not None  # Flag if using temp file
            }
            
            self.logger.info(f"Started audio playback (ID: {playback_id})")
            
            return {
                'playback_id': playback_id,
                'start_time': self.active_playbacks[playback_id]['start_time'],
                'audio_file': audio_file,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Audio playback start failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _start_audio_playback(
            self,
            audio_file: str,
            volume: float = 1.0,
            loop: bool = False
    ) -> Any:
        """
        Start actual audio playback.

        Args:
            audio_file: Path to audio file
            volume: Playback volume (0.0 to 1.0)
            loop: Whether to loop playback

        Returns:
            Playback process or object
        """
        try:
            import subprocess
            
            # Check if file exists
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Determine file type
            _, ext = os.path.splitext(audio_file)
            ext = ext.lower()
            
            # Use appropriate player based on file type
            if ext in ['.wav', '.wave']:
                # Use aplay for WAV files
                cmd = ['aplay']
                
                # Add loop parameter if needed
                if loop:
                    cmd.append('--loop=0')  # 0 means infinite
                
                # Add file path
                cmd.append(audio_file)
                
            else:
                # Use ffplay for other formats
                cmd = ['ffplay', '-nodisp', '-autoexit']
                
                # Add loop parameter if needed
                if loop:
                    cmd.extend(['-loop', '0'])  # 0 means infinite
                
                # Add volume parameter
                cmd.extend(['-volume', str(int(volume * 100))])
                
                # Add file path
                cmd.append(audio_file)
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start audio playback: {e}")
            return None

    async def stop_playback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stop audio playback.

        Args:
            params: Command parameters including playback_id

        Returns:
            Playback stop result
        """
        try:
            playback_id = params.get('playback_id')
            
            if not playback_id or playback_id not in self.active_playbacks:
                return {'error': 'Invalid playback ID', 'status': 'error'}
            
            playback = self.active_playbacks[playback_id]
            duration = time.time() - playback['start_time']
            
            # Stop the playback
            await self._stop_audio_playback(playback)
            
            # Clean up temporary file if used
            if playback.get('temp_file') and os.path.exists(playback['audio_file']):
                try:
                    os.remove(playback['audio_file'])
                    self.logger.info(f"Removed temporary file: {playback['audio_file']}")
                except Exception as e:
                    self.logger.error(f"Failed to remove temporary file: {e}")
            
            # Remove from active playbacks
            del self.active_playbacks[playback_id]
            
            self.logger.info(f"Stopped audio playback (ID: {playback_id}, duration: {duration:.2f}s)")
            
            return {
                'playback_id': playback_id,
                'duration': duration,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Audio playback stop failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _stop_audio_playback(self, playback: Dict[str, Any]) -> None:
        """
        Stop actual audio playback.

        Args:
            playback: Playback information
        """
        try:
            if 'process' in playback and playback['process']:
                process = playback['process']
                
                # Terminate the process
                process.terminate()
                
                try:
                    process.wait(timeout=5)
                except:
                    # Force kill if termination times out
                    process.kill()
                    
        except Exception as e:
            self.logger.error(f"Error stopping playback: {e}")

    async def set_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set system volume.

        Args:
            params: Command parameters including volume level

        Returns:
            Volume set result
        """
        try:
            volume = params.get('volume', 1.0)
            
            # Ensure volume is in valid range
            volume = max(0.0, min(1.0, volume))
            
            self.logger.info(f"Setting system volume to {volume:.2f}")
            
            # Set system volume using amixer
            import subprocess
            
            # Convert to percentage for amixer
            volume_percent = int(volume * 100)
            
            # Run amixer command
            cmd = ['amixer', 'sset', 'Master', f'{volume_percent}%']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to set volume: {result.stderr}")
                return {'error': result.stderr, 'status': 'error'}
            
            self.logger.info(f"Volume set to {volume_percent}%")
            
            return {
                'volume': volume,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Set volume failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def get_volume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current system volume.

        Args:
            params: Command parameters

        Returns:
            Current volume level
        """
        try:
            self.logger.info("Getting system volume")
            
            # Get system volume using amixer
            import subprocess
            import re
            
            # Run amixer command
            cmd = ['amixer', 'get', 'Master']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to get volume: {result.stderr}")
                return {'error': result.stderr, 'status': 'error'}
            
            # Parse volume from output
            volume_match = re.search(r'(\d+)%', result.stdout)
            
            if volume_match:
                volume_percent = int(volume_match.group(1))
                volume = volume_percent / 100.0
                
                self.logger.info(f"Current volume: {volume_percent}%")
                
                return {
                    'volume': volume,
                    'status': 'success'
                }
            else:
                self.logger.error("Failed to parse volume from amixer output")
                return {'error': 'Failed to parse volume', 'status': 'error'}
            
        except Exception as e:
            self.logger.error(f"Get volume failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def start(self):
        """
        Start the speaker server.
        """
        try:
            # Set up speaker device
            if not await self.setup_speaker_device():
                self.logger.error("Failed to set up speaker device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi Speaker Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi Speaker server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Speaker Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    server = RPiSpeakerServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
