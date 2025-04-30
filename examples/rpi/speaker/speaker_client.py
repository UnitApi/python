#!/usr/bin/env python3
"""
Raspberry Pi Speaker Client Example

This script demonstrates how to use the Raspberry Pi Speaker with UnitAPI.
It shows how to play audio files and control volume.
"""

import asyncio
import argparse
import logging
import time
import os
import base64
from typing import Dict, Any, Optional, List

from unitapi.core.client import UnitAPIClient


class RPiSpeakerExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Speaker example.

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
        
        # Speaker device ID
        self.speaker_device_id = None

    async def discover_speaker(self) -> bool:
        """
        Discover Raspberry Pi Speaker.

        Returns:
            Success status
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
                    speaker_type = speaker.get('metadata', {}).get('speaker_type', 'unknown')
                    self.logger.info(f"Speaker {i+1}: {speaker.get('name')} ({speaker_type}) (ID: {speaker.get('device_id')})")
                
                # Look for Raspberry Pi speaker specifically
                rpi_speakers = [
                    speaker for speaker in speakers
                    if 'raspberry' in speaker.get('name', '').lower() or 
                       'rpi' in speaker.get('name', '').lower() or
                       'raspberry' in str(speaker.get('metadata', {})).lower() or
                       'rpi' in str(speaker.get('metadata', {})).lower()
                ]
                
                if rpi_speakers:
                    # Use the first Raspberry Pi speaker
                    self.speaker_device_id = rpi_speakers[0].get('device_id')
                    self.logger.info(f"Using Raspberry Pi Speaker: {rpi_speakers[0].get('name')}")
                else:
                    # Use the first available speaker
                    self.speaker_device_id = speakers[0].get('device_id')
                    self.logger.info(f"No specific Raspberry Pi Speaker found. Using: {speakers[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No speakers found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover speaker: {e}")
            return False

    async def play_audio_file(
            self,
            audio_file: str,
            volume: float = 1.0,
            loop: bool = False,
            wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Play an audio file through the Raspberry Pi Speaker.

        Args:
            audio_file: Path to audio file
            volume: Playback volume (0.0 to 1.0)
            loop: Whether to loop playback
            wait_for_completion: Whether to wait for playback to complete

        Returns:
            Playback result
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_file):
                self.logger.error(f"Audio file not found: {audio_file}")
                return {'error': f"Audio file not found: {audio_file}", 'status': 'error'}
            
            self.logger.info(f"Playing audio file: {audio_file} (volume: {volume:.2f}, loop: {loop})")
            
            # Start playback
            result = await self.client.execute_command(
                device_id=self.speaker_device_id,
                command='play_audio',
                params={
                    'audio_file': audio_file,
                    'volume': volume,
                    'loop': loop
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Playback start failed: {result['error']}")
                return result
                
            playback_id = result.get('playback_id')
            self.logger.info(f"Playback started (ID: {playback_id})")
            
            # Wait for playback to complete if requested
            if wait_for_completion and not loop:
                # Estimate playback duration based on file type
                duration = self._estimate_audio_duration(audio_file)
                
                if duration > 0:
                    self.logger.info(f"Waiting for playback to complete (estimated duration: {duration:.1f}s)")
                    await asyncio.sleep(duration + 0.5)  # Add a small buffer
                    
                    # Stop playback
                    stop_result = await self.client.execute_command(
                        device_id=self.speaker_device_id,
                        command='stop_playback',
                        params={'playback_id': playback_id}
                    )
                    
                    if 'error' in stop_result:
                        self.logger.error(f"Playback stop failed: {stop_result['error']}")
                    else:
                        self.logger.info(f"Playback completed (duration: {stop_result.get('duration', 0):.2f}s)")
                    
                    return stop_result
            
            # Return the start result
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to play audio file: {e}")
            return {'error': str(e), 'status': 'error'}

    def _estimate_audio_duration(self, audio_file: str) -> float:
        """
        Estimate audio file duration.

        Args:
            audio_file: Path to audio file

        Returns:
            Estimated duration in seconds
        """
        try:
            # Try to use ffprobe to get duration
            import subprocess
            import json
            
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return duration
            
            # Fall back to wave module for WAV files
            _, ext = os.path.splitext(audio_file)
            if ext.lower() in ['.wav', '.wave']:
                import wave
                
                with wave.open(audio_file, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
                    return duration
            
            # Return a default duration
            return 10.0
            
        except Exception as e:
            self.logger.error(f"Failed to estimate audio duration: {e}")
            return 10.0  # Default duration

    async def play_audio_data(
            self,
            audio_data: bytes,
            volume: float = 1.0,
            loop: bool = False,
            wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Play audio data through the Raspberry Pi Speaker.

        Args:
            audio_data: Raw audio data (WAV format)
            volume: Playback volume (0.0 to 1.0)
            loop: Whether to loop playback
            wait_for_completion: Whether to wait for playback to complete

        Returns:
            Playback result
        """
        try:
            self.logger.info(f"Playing audio data ({len(audio_data)} bytes, volume: {volume:.2f}, loop: {loop})")
            
            # Encode audio data as base64
            audio_data_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Start playback
            result = await self.client.execute_command(
                device_id=self.speaker_device_id,
                command='play_audio',
                params={
                    'audio_data': audio_data_b64,
                    'volume': volume,
                    'loop': loop
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Playback start failed: {result['error']}")
                return result
                
            playback_id = result.get('playback_id')
            self.logger.info(f"Playback started (ID: {playback_id})")
            
            # Wait for playback to complete if requested
            if wait_for_completion and not loop:
                # Estimate duration based on data size (very rough estimate)
                duration = len(audio_data) / (44100 * 2 * 2)  # Assuming 44.1kHz, 16-bit, stereo
                
                self.logger.info(f"Waiting for playback to complete (estimated duration: {duration:.1f}s)")
                await asyncio.sleep(duration + 0.5)  # Add a small buffer
                
                # Stop playback
                stop_result = await self.client.execute_command(
                    device_id=self.speaker_device_id,
                    command='stop_playback',
                    params={'playback_id': playback_id}
                )
                
                if 'error' in stop_result:
                    self.logger.error(f"Playback stop failed: {stop_result['error']}")
                else:
                    self.logger.info(f"Playback completed (duration: {stop_result.get('duration', 0):.2f}s)")
                
                return stop_result
            
            # Return the start result
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to play audio data: {e}")
            return {'error': str(e), 'status': 'error'}

    async def stop_playback(self, playback_id: str) -> Dict[str, Any]:
        """
        Stop audio playback.

        Args:
            playback_id: Playback ID to stop

        Returns:
            Playback stop result
        """
        try:
            self.logger.info(f"Stopping playback (ID: {playback_id})")
            
            # Stop playback
            result = await self.client.execute_command(
                device_id=self.speaker_device_id,
                command='stop_playback',
                params={'playback_id': playback_id}
            )
            
            if 'error' in result:
                self.logger.error(f"Playback stop failed: {result['error']}")
            else:
                self.logger.info(f"Playback stopped (duration: {result.get('duration', 0):.2f}s)")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to stop playback: {e}")
            return {'error': str(e), 'status': 'error'}

    async def set_volume(self, volume: float) -> Dict[str, Any]:
        """
        Set system volume.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            Volume set result
        """
        try:
            # Ensure volume is in valid range
            volume = max(0.0, min(1.0, volume))
            
            self.logger.info(f"Setting volume to {volume:.2f}")
            
            # Set volume
            result = await self.client.execute_command(
                device_id=self.speaker_device_id,
                command='set_volume',
                params={'volume': volume}
            )
            
            if 'error' in result:
                self.logger.error(f"Set volume failed: {result['error']}")
            else:
                self.logger.info(f"Volume set to {volume:.2f}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to set volume: {e}")
            return {'error': str(e), 'status': 'error'}

    async def get_volume(self) -> Dict[str, Any]:
        """
        Get current system volume.

        Returns:
            Current volume level
        """
        try:
            self.logger.info("Getting current volume")
            
            # Get volume
            result = await self.client.execute_command(
                device_id=self.speaker_device_id,
                command='get_volume',
                params={}
            )
            
            if 'error' in result:
                self.logger.error(f"Get volume failed: {result['error']}")
            else:
                volume = result.get('volume', 0)
                self.logger.info(f"Current volume: {volume:.2f}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to get volume: {e}")
            return {'error': str(e), 'status': 'error'}

    async def play_tone(
            self,
            frequency: float = 440.0,
            duration: float = 1.0,
            volume: float = 0.5
    ) -> Dict[str, Any]:
        """
        Play a simple tone through the speaker.

        Args:
            frequency: Tone frequency in Hz
            duration: Tone duration in seconds
            volume: Playback volume (0.0 to 1.0)

        Returns:
            Playback result
        """
        try:
            self.logger.info(f"Generating {frequency}Hz tone for {duration}s at volume {volume:.2f}")
            
            # Generate a simple sine wave tone
            import numpy as np
            import wave
            import io
            
            # Generate tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t) * volume
            
            # Apply fade in/out to avoid clicks
            fade_samples = int(sample_rate * 0.01)  # 10ms fade
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            if len(tone) > 2 * fade_samples:
                tone[:fade_samples] *= fade_in
                tone[-fade_samples:] *= fade_out
            
            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16)
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            # Get WAV data
            buffer.seek(0)
            wav_data = buffer.read()
            
            # Play the tone
            return await self.play_audio_data(wav_data, volume=1.0)
                
        except Exception as e:
            self.logger.error(f"Failed to play tone: {e}")
            return {'error': str(e), 'status': 'error'}

    async def play_sequence(
            self,
            notes: List[Dict[str, Any]],
            volume: float = 0.5
    ) -> Dict[str, Any]:
        """
        Play a sequence of tones (simple melody).

        Args:
            notes: List of note dictionaries with frequency and duration
            volume: Playback volume (0.0 to 1.0)

        Returns:
            Playback result
        """
        try:
            self.logger.info(f"Playing sequence of {len(notes)} notes")
            
            # Play each note in sequence
            for i, note in enumerate(notes):
                frequency = note.get('frequency', 440.0)
                duration = note.get('duration', 0.5)
                
                self.logger.info(f"Playing note {i+1}/{len(notes)}: {frequency}Hz for {duration}s")
                
                # Play the note
                await self.play_tone(frequency, duration, volume)
                
                # Small pause between notes
                await asyncio.sleep(0.05)
            
            self.logger.info("Sequence playback completed")
            
            return {'status': 'success'}
                
        except Exception as e:
            self.logger.error(f"Failed to play sequence: {e}")
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi Speaker example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Speaker Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--audio-file', help='Audio file to play')
    parser.add_argument('--volume', type=float, default=0.8, help='Playback volume (0.0 to 1.0)')
    parser.add_argument('--loop', action='store_true', help='Loop audio playback')
    parser.add_argument('--demo', choices=['file', 'tone', 'melody', 'volume'], 
                        default='file', help='Demo to run')
    parser.add_argument('--frequency', type=float, default=440.0, help='Tone frequency in Hz')
    parser.add_argument('--duration', type=float, default=1.0, help='Tone duration in seconds')
    
    args = parser.parse_args()
    
    example = RPiSpeakerExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover speaker
    if not await example.discover_speaker():
        print("Failed to discover Raspberry Pi Speaker. Make sure the UnitAPI server is running and the speaker is connected.")
        return
    
    # Run the selected demo
    if args.demo == 'file':
        if not args.audio_file:
            print("Please specify an audio file with --audio-file")
            return
            
        await example.play_audio_file(
            audio_file=args.audio_file,
            volume=args.volume,
            loop=args.loop
        )
        
    elif args.demo == 'tone':
        await example.play_tone(
            frequency=args.frequency,
            duration=args.duration,
            volume=args.volume
        )
        
    elif args.demo == 'melody':
        # Play a simple melody (C major scale)
        notes = [
            {'frequency': 261.63, 'duration': 0.5},  # C4
            {'frequency': 293.66, 'duration': 0.5},  # D4
            {'frequency': 329.63, 'duration': 0.5},  # E4
            {'frequency': 349.23, 'duration': 0.5},  # F4
            {'frequency': 392.00, 'duration': 0.5},  # G4
            {'frequency': 440.00, 'duration': 0.5},  # A4
            {'frequency': 493.88, 'duration': 0.5},  # B4
            {'frequency': 523.25, 'duration': 1.0},  # C5
        ]
        
        await example.play_sequence(notes, volume=args.volume)
        
    elif args.demo == 'volume':
        # Get current volume
        volume_result = await example.get_volume()
        current_volume = volume_result.get('volume', 0.5)
        
        print(f"Current volume: {current_volume:.2f}")
        
        # Set new volume
        await example.set_volume(args.volume)
        
        # Play a test tone
        await example.play_tone(frequency=440.0, duration=1.0)
        
        # Restore original volume
        await example.set_volume(current_volume)


if __name__ == "__main__":
    asyncio.run(main())
