#!/usr/bin/env python3
"""
Speaker Playback Example (Fixed)

This script demonstrates how to send audio to a local or remote speaker.
Uses the fixed client implementation with WebSocket support.
"""

import asyncio
import argparse
import logging
import numpy as np
import base64
from typing import Optional

# Import the fixed client instead of the original one
from unitapi.core.client_fixed import UnitAPIClient


class SpeakerPlaybackExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize speaker playback example.

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

        # UnitAPI client (using the fixed implementation)
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )

    async def list_speakers(self):
        """
        List available speakers.

        Returns:
            List of speaker devices
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for speaker devices
            speakers = [
                device for device in devices
                if device.get('type') == 'speaker'
            ]
            
            if speakers:
                self.logger.info(f"Found {len(speakers)} speaker(s)")
                for i, speaker in enumerate(speakers):
                    self.logger.info(f"Speaker {i+1}: {speaker.get('name')} (ID: {speaker.get('device_id')})")
            else:
                self.logger.warning("No speakers found")
                
            return speakers
            
        except Exception as e:
            self.logger.error(f"Failed to list speakers: {e}")
            return []

    async def play_audio_file(self, device_id: str, file_path: str) -> bool:
        """
        Play audio from a file on a speaker.

        Args:
            device_id: Speaker device ID
            file_path: Path to audio file

        Returns:
            Success status
        """
        try:
            # Read audio file
            with open(file_path, 'rb') as f:
                audio_data = f.read()
                
            # Convert to base64
            base64_audio = base64.b64encode(audio_data).decode()
            
            # Send to speaker
            result = await self.client.execute_command(
                device_id=device_id,
                command='play_audio',
                params={'base64_data': base64_audio}
            )
            
            if result.get('status') == 'success':
                self.logger.info(f"Audio playback successful on device {device_id}")
                return True
            else:
                self.logger.error(f"Audio playback failed: {result.get('message')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}")
            return False

    async def play_generated_audio(
            self,
            device_id: str,
            duration: float = 3.0,
            frequency: float = 440.0
    ) -> bool:
        """
        Play generated audio tone on a speaker.

        Args:
            device_id: Speaker device ID
            duration: Audio duration in seconds
            frequency: Tone frequency in Hz

        Returns:
            Success status
        """
        try:
            # Generate a sine wave tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            # Convert to float32 and then to bytes
            audio_bytes = tone.astype(np.float32).tobytes()
            
            # Convert to base64
            base64_audio = base64.b64encode(audio_bytes).decode()
            
            # Send to speaker
            result = await self.client.execute_command(
                device_id=device_id,
                command='play_audio',
                params={
                    'base64_data': base64_audio,
                    'sample_rate': sample_rate,
                    'channels': 1
                }
            )
            
            if result.get('status') == 'success':
                self.logger.info(f"Generated audio playback successful on device {device_id}")
                return True
            else:
                self.logger.error(f"Generated audio playback failed: {result.get('message')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to play generated audio: {e}")
            return False

    async def play_local_audio(self, device_index: Optional[int] = None):
        """
        Play audio directly on a local speaker using PyAudio.

        Args:
            device_index: PyAudio device index (None for default)
        """
        try:
            import pyaudio
            import time
            
            # Generate a simple tone
            sample_rate = 44100
            duration = 3  # seconds
            frequency = 440  # Hz (A4 note)
            
            # Generate samples
            samples = 0.5 * np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate)
            samples = samples.astype(np.float32)
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # If no device index specified, list available output devices
            if device_index is None:
                info = p.get_host_api_info_by_index(0)
                num_devices = info.get('deviceCount')
                
                # Find output devices
                output_devices = []
                for i in range(num_devices):
                    device_info = p.get_device_info_by_index(i)
                    if device_info.get('maxOutputChannels') > 0:
                        output_devices.append((i, device_info.get('name')))
                
                if not output_devices:
                    self.logger.error("No output devices found")
                    p.terminate()
                    return
                
                # Use the first output device
                device_index = output_devices[0][0]
                self.logger.info(f"Using output device: {output_devices[0][1]} (index: {device_index})")
            
            # Open stream
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                output=True,
                output_device_index=device_index
            )
            
            # Play the tone
            self.logger.info(f"Playing {frequency}Hz tone for {duration} seconds...")
            stream.write(samples.tobytes())
            
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            self.logger.info("Audio playback completed")
            
        except ImportError:
            self.logger.error("PyAudio not available for local audio playback")
        except Exception as e:
            self.logger.error(f"Failed to play local audio: {e}")


async def main():
    """
    Run the speaker playback example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Speaker Playback Example (Fixed)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--local', action='store_true', help='Use local speaker directly')
    parser.add_argument('--device-index', type=int, help='Local speaker device index')
    parser.add_argument('--file', help='Audio file to play')
    parser.add_argument('--frequency', type=float, default=440.0, help='Tone frequency in Hz')
    parser.add_argument('--duration', type=float, default=3.0, help='Audio duration in seconds')
    parser.add_argument('--list-only', action='store_true', help='Only list speakers without playing audio')
    
    args = parser.parse_args()
    
    example = SpeakerPlaybackExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    if args.local:
        # Play directly on local speaker
        await example.play_local_audio(args.device_index)
    else:
        # List available speakers
        speakers = await example.list_speakers()
        
        if args.list_only:
            # Just list speakers and exit
            if not speakers:
                print("No speakers available. Make sure the device discovery service is running.")
            return
        
        if speakers:
            # Use the first speaker
            speaker_id = speakers[0].get('device_id')
            
            if args.file:
                # Play audio file
                await example.play_audio_file(speaker_id, args.file)
            else:
                # Play generated tone
                await example.play_generated_audio(
                    speaker_id,
                    duration=args.duration,
                    frequency=args.frequency
                )
        else:
            print("No speakers available. Make sure the device discovery service is running.")


if __name__ == "__main__":
    asyncio.run(main())
