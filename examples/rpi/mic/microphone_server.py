#!/usr/bin/env python3
"""
Raspberry Pi Microphone Server Example

This script demonstrates how to create a UnitAPI server that exposes microphone functionality
on a Raspberry Pi. This server can be used with the microphone_client.py client example.
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
from unitapi.devices.microphone import MicrophoneDevice


class RPiMicrophoneServer:
    def __init__(
            self,
            host: str = '0.0.0.0',
            port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Microphone server.

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
        
        # Microphone Device
        self.microphone_device = None
        
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
        if self.microphone_device:
            try:
                # Stop any active recordings
                for recording_id in list(self.active_recordings.keys()):
                    try:
                        await self.stop_recording({'recording_id': recording_id})
                    except Exception as e:
                        self.logger.error(f"Error stopping recording {recording_id}: {e}")
                
                await self.microphone_device.disconnect()
                self.logger.info("Microphone device disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting microphone device: {e}")

    async def setup_microphone_device(self):
        """
        Set up and register the microphone device.

        Returns:
            Success status
        """
        try:
            # Check if microphone is available
            microphone_available = self._check_microphone_available()
            
            if not microphone_available:
                self.logger.warning("No microphone detected. Using virtual microphone.")
            
            # Create microphone device
            self.microphone_device = MicrophoneDevice(
                device_id="microphone_rpi",
                name="Raspberry Pi Microphone",
                metadata={
                    "microphone_type": "raspberry_pi",
                    "virtual": not microphone_available,
                    "sample_rate": 44100,
                    "channels": 1
                }
            )
            
            # Connect the device
            await self.microphone_device.connect()
            
            # Register device with server
            self.server.register_device(
                device_id=self.microphone_device.device_id,
                device_type=self.microphone_device.type,
                metadata=self.microphone_device.metadata
            )
            
            # Register command handlers
            self.server.register_command_handler(
                device_id=self.microphone_device.device_id,
                command="start_recording",
                handler=self.start_recording
            )
            
            self.server.register_command_handler(
                device_id=self.microphone_device.device_id,
                command="stop_recording",
                handler=self.stop_recording
            )
            
            self.server.register_command_handler(
                device_id=self.microphone_device.device_id,
                command="get_audio_level",
                handler=self.get_audio_level
            )
            
            self.logger.info(f"Microphone device registered: {self.microphone_device.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up microphone device: {e}")
            return False

    def _check_microphone_available(self) -> bool:
        """
        Check if a microphone is available.

        Returns:
            True if microphone is available, False otherwise
        """
        try:
            # Try to use PyAudio to detect microphones
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Check if any input devices are available
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    p.terminate()
                    return True
            
            p.terminate()
            return False
            
        except ImportError:
            self.logger.warning("PyAudio not available for microphone detection")
            return False
        except Exception as e:
            self.logger.error(f"Error checking microphone availability: {e}")
            return False

    async def start_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start audio recording from the microphone.

        Args:
            params: Command parameters including sample_rate, channels, format, output_file

        Returns:
            Recording start result with recording ID
        """
        try:
            sample_rate = params.get('sample_rate', 44100)
            channels = params.get('channels', 1)
            audio_format = params.get('format', 'wav')
            output_file = params.get('output_file', f'rpi_audio_{int(time.time())}.{audio_format}')
            duration = params.get('duration', None)  # None for unlimited
            
            self.logger.info(f"Starting audio recording at {sample_rate}Hz with {channels} channel(s)")
            
            # Generate unique recording ID
            recording_id = f"rec_{int(time.time())}_{len(self.active_recordings)}"
            
            # Check if we're using a virtual microphone
            if self.microphone_device.metadata.get('virtual', False):
                # Simulate recording for virtual microphone
                self.active_recordings[recording_id] = {
                    'start_time': time.time(),
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'format': audio_format,
                    'output_file': output_file,
                    'duration': duration,
                    'virtual': True
                }
                
                self.logger.info(f"Started virtual audio recording (ID: {recording_id})")
                
                # If duration is specified, schedule stop
                if duration is not None:
                    asyncio.create_task(self._auto_stop_recording(recording_id, duration))
            else:
                # Start actual recording
                recording_process = await self._start_microphone_recording(
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
                
                self.logger.info(f"Started audio recording (ID: {recording_id})")
                
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
            self.logger.error(f"Audio recording start failed: {e}")
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

    async def _start_microphone_recording(
            self,
            sample_rate: int,
            channels: int,
            audio_format: str,
            output_file: str
    ) -> Any:
        """
        Start actual audio recording from the physical microphone.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            audio_format: Audio format (wav, mp3)
            output_file: Output file path

        Returns:
            Recording process or object
        """
        try:
            import pyaudio
            import wave
            import threading
            import subprocess
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # For WAV format, use PyAudio directly
            if audio_format.lower() == 'wav':
                # PyAudio setup
                p = pyaudio.PyAudio()
                
                # Find input device
                device_index = None
                for i in range(p.get_device_count()):
                    device_info = p.get_device_info_by_index(i)
                    if device_info.get('maxInputChannels') > 0:
                        device_index = i
                        break
                
                # Open stream
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
                
                # Open WAV file
                wf = wave.open(output_file, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                
                # Create stop event
                stop_event = threading.Event()
                
                # Recording thread function
                def record_thread():
                    try:
                        while not stop_event.is_set():
                            data = stream.read(1024, exception_on_overflow=False)
                            wf.writeframes(data)
                    except Exception as e:
                        self.logger.error(f"Error in recording thread: {e}")
                    finally:
                        stream.stop_stream()
                        stream.close()
                        wf.close()
                        p.terminate()
                
                # Start recording thread
                thread = threading.Thread(target=record_thread)
                thread.start()
                
                return {
                    'thread': thread,
                    'stop_event': stop_event,
                    'pyaudio': p,
                    'stream': stream,
                    'wavefile': wf
                }
                
            # For other formats, use arecord and ffmpeg
            else:
                # Use arecord for capture and pipe to ffmpeg for encoding
                cmd = [
                    'arecord',
                    '-f', 'S16_LE',
                    '-c', str(channels),
                    '-r', str(sample_rate),
                    '-D', 'plughw:0,0',
                    '-t', 'wav',
                    '-'
                ]
                
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
                
                # Start arecord process
                arecord_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
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
            self.logger.error(f"Failed to start microphone recording: {e}")
            
            # Return None for virtual recording
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
                await self._stop_microphone_recording(recording)
            
            # Remove from active recordings
            del self.active_recordings[recording_id]
            
            self.logger.info(f"Stopped audio recording (ID: {recording_id}, duration: {duration:.2f}s)")
            
            return {
                'recording_id': recording_id,
                'duration': duration,
                'output_file': recording['output_file'],
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Audio recording stop failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _stop_microphone_recording(self, recording: Dict[str, Any]) -> None:
        """
        Stop actual audio recording.

        Args:
            recording: Recording information
        """
        try:
            if 'thread' in recording and 'stop_event' in recording:
                # Stop PyAudio recording thread
                recording['stop_event'].set()
                recording['thread'].join(timeout=5)
                
                # Close resources if still open
                if 'stream' in recording and recording['stream']:
                    try:
                        recording['stream'].stop_stream()
                        recording['stream'].close()
                    except:
                        pass
                
                if 'pyaudio' in recording and recording['pyaudio']:
                    try:
                        recording['pyaudio'].terminate()
                    except:
                        pass
                
                if 'wavefile' in recording and recording['wavefile']:
                    try:
                        recording['wavefile'].close()
                    except:
                        pass
                        
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
        Generate a test audio file for virtual microphone.

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
            
            # Duplicate for stereo if needed
            if channels == 2:
                audio = np.column_stack((audio, audio))
            
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
        Get current audio input level.

        Args:
            params: Command parameters

        Returns:
            Audio level result
        """
        try:
            # Check if we're using a virtual microphone
            if self.microphone_device.metadata.get('virtual', False):
                # Generate random audio level for virtual microphone
                import random
                level = random.uniform(0.0, 1.0)
                
                self.logger.debug(f"Virtual microphone audio level: {level:.2f}")
                
                return {
                    'level': level,
                    'status': 'success'
                }
            else:
                # Get actual audio level from microphone
                level = await self._get_microphone_level()
                
                self.logger.debug(f"Microphone audio level: {level:.2f}")
                
                return {
                    'level': level,
                    'status': 'success'
                }
                
        except Exception as e:
            self.logger.error(f"Get audio level failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _get_microphone_level(self) -> float:
        """
        Get actual audio level from microphone.

        Returns:
            Audio level (0.0 to 1.0)
        """
        try:
            import pyaudio
            import numpy as np
            
            # PyAudio setup
            p = pyaudio.PyAudio()
            
            # Find input device
            device_index = None
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    device_index = i
                    break
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
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
            
            # Calculate RMS level
            rms = np.sqrt(np.mean(np.square(audio_data)))
            
            # Normalize to 0.0-1.0 range (assuming 16-bit audio)
            level = min(1.0, rms / 32767)
            
            return level
            
        except Exception as e:
            self.logger.error(f"Failed to get microphone level: {e}")
            
            # Return random level as fallback
            import random
            return random.uniform(0.0, 1.0)

    async def start(self):
        """
        Start the microphone server.
        """
        try:
            # Set up microphone device
            if not await self.setup_microphone_device():
                self.logger.error("Failed to set up microphone device, exiting")
                return
            
            # Start UnitAPI server
            server_task = asyncio.create_task(self.server.start())
            
            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket.create_server())
            
            self.logger.info(f"Raspberry Pi Microphone Server started on {self.server.host}:{self.server.port}")
            self.logger.info("Press Ctrl+C to stop the server")
            
            # Wait for servers
            await asyncio.gather(server_task, websocket_task)
            
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            await self._cleanup()


async def main():
    """
    Run the Raspberry Pi Microphone server.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Microphone Server')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=7890, help='Server port')
    
    args = parser.parse_args()
    
    server = RPiMicrophoneServer(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
