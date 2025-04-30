#!/usr/bin/env python3
"""
Raspberry Pi Microphone Client Example

This script demonstrates how to use the Raspberry Pi Microphone with UnitAPI.
It shows how to record audio and monitor audio levels.
"""

import asyncio
import argparse
import logging
import time
import os
from typing import Dict, Any, Optional

from unitapi.core.client import UnitAPIClient


class RPiMicrophoneExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Microphone example.

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
        
        # Microphone device ID
        self.microphone_device_id = None

    async def discover_microphone(self) -> bool:
        """
        Discover Raspberry Pi Microphone.

        Returns:
            Success status
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
                    mic_type = mic.get('metadata', {}).get('microphone_type', 'unknown')
                    self.logger.info(f"Microphone {i+1}: {mic.get('name')} ({mic_type}) (ID: {mic.get('device_id')})")
                
                # Look for Raspberry Pi microphone specifically
                rpi_mics = [
                    mic for mic in microphones
                    if 'raspberry' in mic.get('name', '').lower() or 
                       'rpi' in mic.get('name', '').lower() or
                       'raspberry' in str(mic.get('metadata', {})).lower() or
                       'rpi' in str(mic.get('metadata', {})).lower()
                ]
                
                if rpi_mics:
                    # Use the first Raspberry Pi microphone
                    self.microphone_device_id = rpi_mics[0].get('device_id')
                    self.logger.info(f"Using Raspberry Pi Microphone: {rpi_mics[0].get('name')}")
                else:
                    # Use the first available microphone
                    self.microphone_device_id = microphones[0].get('device_id')
                    self.logger.info(f"No specific Raspberry Pi Microphone found. Using: {microphones[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No microphones found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover microphone: {e}")
            return False

    async def record_audio(
            self,
            output_file: str = 'rpi_recording.wav',
            duration: float = 5.0,
            sample_rate: int = 44100,
            channels: int = 1,
            audio_format: str = 'wav'
    ) -> Dict[str, Any]:
        """
        Record audio from the Raspberry Pi Microphone.

        Args:
            output_file: Path to save the audio
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            audio_format: Audio format (wav, mp3)

        Returns:
            Recording result
        """
        try:
            self.logger.info(f"Recording {duration}s audio at {sample_rate}Hz with {channels} channel(s)")
            
            # Start recording
            result = await self.client.execute_command(
                device_id=self.microphone_device_id,
                command='start_recording',
                params={
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'format': audio_format,
                    'output_file': output_file,
                    'duration': duration
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Recording start failed: {result['error']}")
                return result
                
            recording_id = result.get('recording_id')
            self.logger.info(f"Recording started (ID: {recording_id})")
            
            # Wait for the recording to complete (if duration is specified)
            if duration is not None:
                self.logger.info(f"Recording for {duration} seconds...")
                
                # Show progress
                for i in range(int(duration)):
                    await asyncio.sleep(1)
                    self.logger.info(f"Recording: {i+1}/{int(duration)}s")
                    
                    # Get audio level every second
                    level_result = await self.client.execute_command(
                        device_id=self.microphone_device_id,
                        command='get_audio_level',
                        params={}
                    )
                    
                    if 'error' not in level_result:
                        level = level_result.get('level', 0)
                        self._print_level_meter(level)
                
                # Wait a bit more to ensure recording is complete
                await asyncio.sleep(0.5)
                
                # Get the recording result
                stop_result = await self.client.execute_command(
                    device_id=self.microphone_device_id,
                    command='stop_recording',
                    params={'recording_id': recording_id}
                )
                
                if 'error' in stop_result:
                    self.logger.error(f"Recording stop failed: {stop_result['error']}")
                    return stop_result
                    
                self.logger.info(f"Recording completed and saved to {output_file}")
                return stop_result
            else:
                # For manual stop, return the start result
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to record audio: {e}")
            return {'error': str(e), 'status': 'error'}

    def _print_level_meter(self, level: float, width: int = 40):
        """
        Print a text-based level meter.

        Args:
            level: Audio level (0.0 to 1.0)
            width: Meter width in characters
        """
        # Calculate number of filled blocks
        filled = int(level * width)
        
        # Create meter string
        meter = '█' * filled + '░' * (width - filled)
        
        # Print meter with level percentage
        print(f"Level: [{meter}] {int(level * 100)}%")

    async def monitor_audio_levels(
            self,
            duration: float = 10.0,
            interval: float = 0.1
    ) -> Dict[str, Any]:
        """
        Monitor audio input levels.

        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds

        Returns:
            Monitoring result
        """
        try:
            self.logger.info(f"Monitoring audio levels for {duration} seconds")
            
            # Record start time
            start_time = time.time()
            
            # Store level readings
            readings = []
            
            # Monitor loop
            while time.time() - start_time < duration:
                # Get audio level
                result = await self.client.execute_command(
                    device_id=self.microphone_device_id,
                    command='get_audio_level',
                    params={}
                )
                
                if 'error' in result:
                    self.logger.error(f"Get audio level failed: {result['error']}")
                else:
                    level = result.get('level', 0)
                    elapsed = time.time() - start_time
                    
                    # Store reading
                    readings.append({
                        'time': elapsed,
                        'level': level
                    })
                    
                    # Print level meter
                    self._print_level_meter(level)
                
                # Wait for next interval
                await asyncio.sleep(interval)
            
            self.logger.info(f"Audio level monitoring completed. Collected {len(readings)} readings.")
            
            return {
                'readings': readings,
                'duration': duration,
                'interval': interval,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor audio levels: {e}")
            return {'error': str(e), 'status': 'error'}

    async def voice_activity_detection(
            self,
            threshold: float = 0.1,
            duration: float = 30.0,
            min_silence: float = 1.0,
            min_speech: float = 0.5
    ) -> Dict[str, Any]:
        """
        Perform simple voice activity detection.

        Args:
            threshold: Audio level threshold (0.0 to 1.0)
            duration: Monitoring duration in seconds
            min_silence: Minimum silence duration in seconds
            min_speech: Minimum speech duration in seconds

        Returns:
            Voice activity detection result
        """
        try:
            self.logger.info(f"Voice activity detection for {duration} seconds (threshold: {threshold})")
            
            # Record start time
            start_time = time.time()
            
            # Track speech segments
            is_speech = False
            speech_start = None
            speech_segments = []
            
            # Track silence duration
            silence_start = time.time()
            
            # Monitor loop
            while time.time() - start_time < duration:
                # Get audio level
                result = await self.client.execute_command(
                    device_id=self.microphone_device_id,
                    command='get_audio_level',
                    params={}
                )
                
                if 'error' not in result:
                    level = result.get('level', 0)
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    # Print level meter
                    self._print_level_meter(level)
                    
                    # Check if level exceeds threshold
                    if level >= threshold:
                        # Reset silence start time
                        silence_start = current_time
                        
                        # Start new speech segment if not already in one
                        if not is_speech:
                            speech_start = elapsed
                            is_speech = True
                            self.logger.info(f"Speech detected at {elapsed:.2f}s")
                    else:
                        # Check if silence duration exceeds minimum
                        silence_duration = current_time - silence_start
                        
                        if is_speech and silence_duration >= min_silence:
                            # End speech segment
                            speech_end = elapsed - silence_duration
                            speech_duration = speech_end - speech_start
                            
                            # Only record if speech duration exceeds minimum
                            if speech_duration >= min_speech:
                                speech_segments.append({
                                    'start': speech_start,
                                    'end': speech_end,
                                    'duration': speech_duration
                                })
                                self.logger.info(f"Speech ended at {speech_end:.2f}s (duration: {speech_duration:.2f}s)")
                            
                            is_speech = False
                
                # Wait for next sample
                await asyncio.sleep(0.1)
            
            # Handle final speech segment if still active
            if is_speech:
                speech_end = time.time() - start_time
                speech_duration = speech_end - speech_start
                
                if speech_duration >= min_speech:
                    speech_segments.append({
                        'start': speech_start,
                        'end': speech_end,
                        'duration': speech_duration
                    })
                    self.logger.info(f"Speech ended at {speech_end:.2f}s (duration: {speech_duration:.2f}s)")
            
            self.logger.info(f"Voice activity detection completed. Detected {len(speech_segments)} speech segments.")
            
            return {
                'speech_segments': speech_segments,
                'threshold': threshold,
                'duration': duration,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform voice activity detection: {e}")
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi Microphone example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Microphone Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--demo', choices=['record', 'monitor', 'vad'], 
                        default='record', help='Demo to run')
    parser.add_argument('--duration', type=float, default=5.0, help='Recording/monitoring duration in seconds')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Audio sample rate in Hz')
    parser.add_argument('--channels', type=int, default=1, help='Number of audio channels')
    parser.add_argument('--format', choices=['wav', 'mp3'], default='wav', help='Audio format')
    parser.add_argument('--threshold', type=float, default=0.1, help='Voice activity detection threshold')
    
    args = parser.parse_args()
    
    example = RPiMicrophoneExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover microphone
    if not await example.discover_microphone():
        print("Failed to discover Raspberry Pi Microphone. Make sure the UnitAPI server is running and the microphone is connected.")
        return
    
    # Run the selected demo
    if args.demo == 'record':
        output_file = args.output or f'rpi_recording_{int(time.time())}.{args.format}'
        await example.record_audio(
            output_file=output_file,
            duration=args.duration,
            sample_rate=args.sample_rate,
            channels=args.channels,
            audio_format=args.format
        )
        
    elif args.demo == 'monitor':
        await example.monitor_audio_levels(
            duration=args.duration,
            interval=0.1
        )
        
    elif args.demo == 'vad':
        await example.voice_activity_detection(
            threshold=args.threshold,
            duration=args.duration
        )


if __name__ == "__main__":
    asyncio.run(main())
