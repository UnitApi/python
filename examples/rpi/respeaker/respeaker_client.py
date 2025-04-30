#!/usr/bin/env python3
"""
Raspberry Pi ReSpeaker Client Example

This script demonstrates how to use the ReSpeaker microphone array with UnitAPI.
It shows how to record audio, get direction of arrival, and control LEDs.
"""

import asyncio
import argparse
import logging
import time
import os
import base64
from typing import Dict, Any, List, Optional

from unitapi.core.client import UnitAPIClient


class RPiReSpeakerExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi ReSpeaker example.

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
        
        # ReSpeaker device ID
        self.respeaker_device_id = None

    async def discover_respeaker(self) -> bool:
        """
        Discover ReSpeaker microphone array.

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
                
                # Look for ReSpeaker specifically
                respeaker_mics = [
                    mic for mic in microphones
                    if 'respeaker' in mic.get('name', '').lower() or 
                       'respeaker' in str(mic.get('metadata', {})).lower()
                ]
                
                if respeaker_mics:
                    # Use the first ReSpeaker
                    self.respeaker_device_id = respeaker_mics[0].get('device_id')
                    self.logger.info(f"Using ReSpeaker: {respeaker_mics[0].get('name')}")
                else:
                    # Use the first available microphone
                    self.respeaker_device_id = microphones[0].get('device_id')
                    self.logger.info(f"No ReSpeaker found. Using: {microphones[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No microphones found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover ReSpeaker: {e}")
            return False

    async def record_audio(
            self,
            output_file: str = 'respeaker_recording.wav',
            duration: float = 5.0,
            sample_rate: int = 16000,
            channels: int = 1,
            audio_format: str = 'wav'
    ) -> Dict[str, Any]:
        """
        Record audio from the ReSpeaker.

        Args:
            output_file: Path to save the audio
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of audio channels (1 for beamformed, 4 for all mics)
            audio_format: Audio format (wav, mp3)

        Returns:
            Recording result
        """
        try:
            self.logger.info(f"Recording {duration}s audio at {sample_rate}Hz with {channels} channel(s)")
            
            # Start recording
            result = await self.client.execute_command(
                device_id=self.respeaker_device_id,
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
            
            # Show direction during recording
            self.logger.info(f"Recording for {duration} seconds...")
            
            # Show progress and direction
            for i in range(int(duration)):
                await asyncio.sleep(1)
                self.logger.info(f"Recording: {i+1}/{int(duration)}s")
                
                # Get direction every second
                direction_result = await self.client.execute_command(
                    device_id=self.respeaker_device_id,
                    command='get_direction',
                    params={}
                )
                
                if 'error' not in direction_result:
                    angle = direction_result.get('angle', 0)
                    self._print_direction_indicator(angle)
                
                # Get audio level every second
                level_result = await self.client.execute_command(
                    device_id=self.respeaker_device_id,
                    command='get_audio_level',
                    params={}
                )
                
                if 'error' not in level_result:
                    levels = level_result.get('levels', [0])
                    avg_level = level_result.get('average_level', 0)
                    self._print_level_meter(avg_level)
                    
                    # Set LED color based on audio level
                    await self._update_leds_by_level(avg_level)
            
            # Wait a bit more to ensure recording is complete
            await asyncio.sleep(0.5)
            
            # Reset LEDs
            await self.set_led_pattern('solid', 0.5, [0, 0, 255])
            
            # Get the recording result
            stop_result = await self.client.execute_command(
                device_id=self.respeaker_device_id,
                command='stop_recording',
                params={'recording_id': recording_id}
            )
            
            if 'error' in stop_result:
                self.logger.error(f"Recording stop failed: {stop_result['error']}")
                return stop_result
                
            self.logger.info(f"Recording completed and saved to {output_file}")
            return stop_result
                
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

    def _print_direction_indicator(self, angle: int, radius: int = 20):
        """
        Print a text-based direction indicator.

        Args:
            angle: Direction angle in degrees (0-359)
            radius: Radius of the indicator
        """
        import math
        
        # Create a 2D grid
        grid = [[' ' for _ in range(radius*2+1)] for _ in range(radius*2+1)]
        
        # Mark the center
        grid[radius][radius] = '+'
        
        # Calculate the point on the circle
        rad_angle = math.radians(angle)
        x = int(radius * math.sin(rad_angle)) + radius
        y = int(radius * math.cos(rad_angle)) + radius
        
        # Mark the direction
        grid[y][x] = 'O'
        
        # Draw the grid
        print(f"Direction: {angle}°")
        for row in grid:
            print(''.join(row))

    async def _update_leds_by_level(self, level: float) -> None:
        """
        Update LEDs based on audio level.

        Args:
            level: Audio level (0.0 to 1.0)
        """
        # Map level to color (green to red)
        r = int(255 * level)
        g = int(255 * (1 - level))
        b = 0
        
        # Set LED pattern
        await self.set_led_pattern('solid', 1.0, [r, g, b])

    async def monitor_direction(
            self,
            duration: float = 10.0,
            interval: float = 0.1,
            led_feedback: bool = True
    ) -> Dict[str, Any]:
        """
        Monitor direction of arrival.

        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            led_feedback: Whether to update LEDs based on direction

        Returns:
            Monitoring result
        """
        try:
            self.logger.info(f"Monitoring direction for {duration} seconds")
            
            # Record start time
            start_time = time.time()
            
            # Store direction readings
            readings = []
            
            # Monitor loop
            while time.time() - start_time < duration:
                # Get direction
                result = await self.client.execute_command(
                    device_id=self.respeaker_device_id,
                    command='get_direction',
                    params={}
                )
                
                if 'error' in result:
                    self.logger.error(f"Get direction failed: {result['error']}")
                else:
                    angle = result.get('angle', 0)
                    elapsed = time.time() - start_time
                    
                    # Store reading
                    readings.append({
                        'time': elapsed,
                        'angle': angle
                    })
                    
                    # Print direction indicator
                    self._print_direction_indicator(angle)
                    
                    # Update LEDs based on direction if requested
                    if led_feedback:
                        await self._update_leds_by_direction(angle)
                
                # Wait for next interval
                await asyncio.sleep(interval)
            
            # Reset LEDs
            if led_feedback:
                await self.set_led_pattern('solid', 0.5, [0, 0, 255])
            
            self.logger.info(f"Direction monitoring completed. Collected {len(readings)} readings.")
            
            return {
                'readings': readings,
                'duration': duration,
                'interval': interval,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor direction: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _update_leds_by_direction(self, angle: int) -> None:
        """
        Update LEDs based on direction.

        Args:
            angle: Direction angle in degrees (0-359)
        """
        # Map angle to color (hue)
        import colorsys
        
        # Convert angle to hue (0-1)
        hue = angle / 360.0
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        
        # Scale to 0-255
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        
        # Set LED pattern
        await self.set_led_pattern('solid', 1.0, [r, g, b])

    async def set_led_pattern(
            self,
            pattern: str = 'solid',
            brightness: float = 1.0,
            color: List[int] = [0, 0, 255]
    ) -> Dict[str, Any]:
        """
        Set the LED pattern on the ReSpeaker.

        Args:
            pattern: LED pattern ('solid', 'pulse', 'spin', 'custom')
            brightness: LED brightness (0.0 to 1.0)
            color: RGB color as [r, g, b] (0-255)

        Returns:
            LED pattern result
        """
        try:
            self.logger.info(f"Setting LED pattern: {pattern}, brightness: {brightness}, color: {color}")
            
            # Set LED pattern
            result = await self.client.execute_command(
                device_id=self.respeaker_device_id,
                command='set_led_pattern',
                params={
                    'pattern': pattern,
                    'brightness': brightness,
                    'color': color
                }
            )
            
            if 'error' in result:
                self.logger.error(f"Set LED pattern failed: {result['error']}")
            else:
                self.logger.info(f"LED pattern set: {pattern}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Failed to set LED pattern: {e}")
            return {'error': str(e), 'status': 'error'}

    async def led_demo(self, duration: float = 10.0) -> Dict[str, Any]:
        """
        Run a demo of LED patterns.

        Args:
            duration: Demo duration in seconds

        Returns:
            Demo result
        """
        try:
            self.logger.info(f"Running LED pattern demo for {duration} seconds")
            
            # Calculate time per pattern
            patterns = ['solid', 'pulse', 'spin']
            colors = [
                [255, 0, 0],    # Red
                [0, 255, 0],    # Green
                [0, 0, 255],    # Blue
                [255, 255, 0],  # Yellow
                [255, 0, 255],  # Magenta
                [0, 255, 255],  # Cyan
                [255, 255, 255] # White
            ]
            
            # Calculate time per combination
            total_combinations = len(patterns) * len(colors)
            time_per_combo = duration / total_combinations
            
            # Run through all combinations
            for pattern in patterns:
                for color in colors:
                    self.logger.info(f"Setting pattern: {pattern}, color: {color}")
                    
                    # Set the pattern
                    await self.set_led_pattern(pattern, 1.0, color)
                    
                    # Wait for the specified time
                    await asyncio.sleep(time_per_combo)
            
            # Reset to default
            await self.set_led_pattern('solid', 0.5, [0, 0, 255])
            
            self.logger.info("LED pattern demo completed")
            
            return {'status': 'success'}
                
        except Exception as e:
            self.logger.error(f"Failed to run LED demo: {e}")
            return {'error': str(e), 'status': 'error'}

    async def voice_localization_demo(self, duration: float = 30.0) -> Dict[str, Any]:
        """
        Run a voice localization demo.

        Args:
            duration: Demo duration in seconds

        Returns:
            Demo result
        """
        try:
            self.logger.info(f"Running voice localization demo for {duration} seconds")
            self.logger.info("Speak into the microphone to see direction tracking")
            
            # Record start time
            start_time = time.time()
            
            # Store readings
            readings = []
            
            # Set initial LED pattern
            await self.set_led_pattern('solid', 0.5, [0, 0, 255])
            
            # Monitor loop
            while time.time() - start_time < duration:
                # Get audio level
                level_result = await self.client.execute_command(
                    device_id=self.respeaker_device_id,
                    command='get_audio_level',
                    params={}
                )
                
                if 'error' not in level_result:
                    avg_level = level_result.get('average_level', 0)
                    self._print_level_meter(avg_level)
                    
                    # Only get direction if audio level is above threshold
                    if avg_level > 0.1:
                        # Get direction
                        direction_result = await self.client.execute_command(
                            device_id=self.respeaker_device_id,
                            command='get_direction',
                            params={}
                        )
                        
                        if 'error' not in direction_result:
                            angle = direction_result.get('angle', 0)
                            elapsed = time.time() - start_time
                            
                            # Store reading
                            readings.append({
                                'time': elapsed,
                                'angle': angle,
                                'level': avg_level
                            })
                            
                            # Print direction indicator
                            self._print_direction_indicator(angle)
                            
                            # Update LEDs based on direction
                            await self._update_leds_by_direction(angle)
                            
                            self.logger.info(f"Voice detected at {angle}° (level: {avg_level:.2f})")
                
                # Wait for next sample
                await asyncio.sleep(0.1)
            
            # Reset LEDs
            await self.set_led_pattern('solid', 0.5, [0, 0, 255])
            
            self.logger.info(f"Voice localization demo completed. Detected {len(readings)} voice events.")
            
            return {
                'readings': readings,
                'duration': duration,
                'status': 'success'
            }
                
        except Exception as e:
            self.logger.error(f"Failed to run voice localization demo: {e}")
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi ReSpeaker example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi ReSpeaker Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--demo', choices=['record', 'direction', 'led', 'voice'], 
                        default='record', help='Demo to run')
    parser.add_argument('--duration', type=float, default=10.0, help='Demo duration in seconds')
    parser.add_argument('--channels', type=int, default=1, help='Number of audio channels (1 for beamformed, 4 for all mics)')
    parser.add_argument('--sample-rate', type=int, default=16000, help='Audio sample rate in Hz')
    parser.add_argument('--format', choices=['wav', 'mp3'], default='wav', help='Audio format')
    
    args = parser.parse_args()
    
    example = RPiReSpeakerExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover ReSpeaker
    if not await example.discover_respeaker():
        print("Failed to discover ReSpeaker. Make sure the UnitAPI server is running and the ReSpeaker is connected.")
        return
    
    # Run the selected demo
    if args.demo == 'record':
        output_file = args.output or f'respeaker_recording_{int(time.time())}.{args.format}'
        await example.record_audio(
            output_file=output_file,
            duration=args.duration,
            sample_rate=args.sample_rate,
            channels=args.channels,
            audio_format=args.format
        )
        
    elif args.demo == 'direction':
        await example.monitor_direction(
            duration=args.duration,
            interval=0.1,
            led_feedback=True
        )
        
    elif args.demo == 'led':
        await example.led_demo(
            duration=args.duration
        )
        
    elif args.demo == 'voice':
        await example.voice_localization_demo(
            duration=args.duration
        )


if __name__ == "__main__":
    asyncio.run(main())
