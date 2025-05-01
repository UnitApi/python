#!/usr/bin/env python3
"""
Microphone Recording Example

This script demonstrates how to record audio from a local or remote microphone.
"""

import asyncio
import argparse
import logging
import numpy as np
import base64
import wave
import os
from typing import Optional, Dict, Any

from unitapi.core.client import UnitAPIClient


class MicrophoneRecordingExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize microphone recording example.

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

    async def list_microphones(self):
        """
        List available microphones.

        Returns:
            List of microphone devices
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for microphone devices
            microphones = [
                device for device in devices
                if device.get('type') == 'microphone'
            ]
            
            if microphones:
                self.logger.info(f"Found {len(microphones)} microphone(s)")
                for i, mic in enumerate(microphones):
                    self.logger.info(f"Microphone {i+1}: {mic.get('name')} (ID: {mic.get('device_id')})")
            else:
                self.logger.warning("No microphones found")
                
            return microphones
            
        except Exception as e:
            self.logger.error(f"Failed to list microphones: {e}")
            return []

    async def record_from_device(
            self,
            device_id: str,
            duration: int = 5,
            sample_rate: int = 44100,
            output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record audio from a remote microphone device.

        Args:
            device_id: Microphone device ID
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            output_file: Optional path to save the recording

        Returns:
            Recording result
        """
        try:
            self.logger.info(f"Recording {duration} seconds from device {device_id}...")
            
            # Execute record command
            result = await self.client.execute_command(
                device_id=device_id,
                command='record',
                params={
                    'duration': duration,
                    'sample_rate': sample_rate
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Recording failed: {result['error']}")
                return result
                
            self.logger.info("Recording completed successfully")
            
            # Save to file if requested
            if output_file and 'data' in result:
                try:
                    # Decode base64 data if present
                    if isinstance(result['data'], str):
                        audio_data = base64.b64decode(result['data'])
                    else:
                        audio_data = result['data']
                        
                    # Determine file extension
                    _, ext = os.path.splitext(output_file)
                    if not ext:
                        output_file += '.wav'
                        
                    # Save as WAV file
                    if output_file.endswith('.wav'):
                        # Create WAV file
                        with wave.open(output_file, 'wb') as wf:
                            wf.setnchannels(result.get('channels', 2))
                            wf.setsampwidth(2)  # 16-bit
                            wf.setframerate(result.get('sample_rate', sample_rate))
                            wf.writeframes(audio_data)
                    else:
                        # Save raw data
                        with open(output_file, 'wb') as f:
                            f.write(audio_data)
                            
                    self.logger.info(f"Recording saved to {output_file}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to save recording: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to record from device: {e}")
            return {'error': str(e)}

    async def record_local_audio(
            self,
            duration: int = 5,
            sample_rate: int = 44100,
            device_index: Optional[int] = None,
            output_file: Optional[str] = None
    ):
        """
        Record audio directly from a local microphone using PyAudio.

        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            device_index: PyAudio device index (None for default)
            output_file: Optional path to save the recording
        """
        try:
            import pyaudio
            import wave
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # If no device index specified, list available input devices
            if device_index is None:
                info = p.get_host_api_info_by_index(0)
                num_devices = info.get('deviceCount')
                
                # Find input devices
                input_devices = []
                for i in range(num_devices):
                    device_info = p.get_device_info_by_index(i)
                    if device_info.get('maxInputChannels') > 0:
                        input_devices.append((i, device_info.get('name')))
                
                if not input_devices:
                    self.logger.error("No input devices found")
                    p.terminate()
                    return
                
                # Use the first input device
                device_index = input_devices[0][0]
                self.logger.info(f"Using input device: {input_devices[0][1]} (index: {device_index})")
            
            # Set recording parameters
            channels = 1
            chunk = 1024
            
            # Open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk
            )
            
            # Start recording
            self.logger.info(f"Recording {duration} seconds...")
            frames = []
            
            for i in range(0, int(sample_rate / chunk * duration)):
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    self.logger.warning(f"Error reading audio chunk: {e}")
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.logger.info("Recording completed")
            
            # Save to file if requested
            if output_file:
                # Determine file extension
                _, ext = os.path.splitext(output_file)
                if not ext:
                    output_file += '.wav'
                    
                # Save as WAV file
                if output_file.endswith('.wav'):
                    with wave.open(output_file, 'wb') as wf:
                        wf.setnchannels(channels)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(sample_rate)
                        wf.writeframes(b''.join(frames))
                else:
                    # Save raw data
                    with open(output_file, 'wb') as f:
                        f.write(b''.join(frames))
                        
                self.logger.info(f"Recording saved to {output_file}")
            
        except ImportError:
            self.logger.error("PyAudio not available for local audio recording")
        except Exception as e:
            self.logger.error(f"Failed to record local audio: {e}")


async def main():
    """
    Run the microphone recording example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Microphone Recording Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--local', action='store_true', help='Use local microphone directly')
    parser.add_argument('--device-index', type=int, help='Local microphone device index')
    parser.add_argument('--duration', type=int, default=5, help='Recording duration in seconds')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Audio sample rate')
    parser.add_argument('--output', default='recording.wav', help='Output file path')
    
    args = parser.parse_args()
    
    example = MicrophoneRecordingExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    if args.local:
        # Record directly from local microphone
        await example.record_local_audio(
            duration=args.duration,
            sample_rate=args.sample_rate,
            device_index=args.device_index,
            output_file=args.output
        )
    else:
        # List available microphones
        microphones = await example.list_microphones()
        
        if microphones:
            # Use the first microphone
            mic_id = microphones[0].get('device_id')
            
            # Record from the microphone
            await example.record_from_device(
                device_id=mic_id,
                duration=args.duration,
                sample_rate=args.sample_rate,
                output_file=args.output
            )
        else:
            print("No microphones available. Run the device discovery service first.")


if __name__ == "__main__":
    asyncio.run(main())
