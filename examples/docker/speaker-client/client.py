#!/usr/bin/env python3
"""
UnitAPI Speaker Client

This script connects to a remote UnitAPI speaker agent and allows you to
list and test speakers on the remote machine.
"""

import asyncio
import argparse
import logging
import sys
import numpy as np
import base64
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SpeakerClient")

# Check if UnitAPI is installed
try:
    from unitapi.core.client import UnitAPIClient
except ImportError:
    logger.error("UnitAPI not found. Please install UnitAPI first.")
    logger.error("You can install it with: pip install unitapi")
    sys.exit(1)


class SpeakerClient:
    """Client for controlling remote UnitAPI speakers."""

    def __init__(self, server_host: str, server_port: int = 7890):
        """Initialize the speaker client."""
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )
        self.server_host = server_host
        self.server_port = server_port
        logger.info(f"Speaker Client initialized for {server_host}:{server_port}")

    async def list_speakers(self):
        """List all available speakers."""
        try:
            # Get list of speakers from server
            speakers = await self.client.list_devices(device_type="speaker")
            
            if not speakers:
                logger.warning("No speakers found on the server")
                return []
                
            logger.info(f"Found {len(speakers)} speakers")
            return speakers
            
        except Exception as e:
            logger.error(f"Error listing speakers: {e}")
            return []

    async def play_test_tone(self, device_id: str, frequency: float = 440.0, duration: float = 3.0):
        """Play a test tone on a speaker."""
        try:
            # Generate a simple sine wave tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            # Convert to float32 and to bytes
            audio_data = tone.astype(np.float32).tobytes()
            
            # Encode audio data to base64 for transmission
            base64_audio = base64.b64encode(audio_data).decode()
            
            # Send command to play audio
            result = await self.client.execute_command(
                device_id=device_id,
                command="play_audio",
                params={"base64_data": base64_audio}
            )
            
            logger.info(f"Played test tone on {device_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error playing test tone: {e}")
            return {"status": "error", "message": str(e)}

    async def play_audio_file(self, device_id: str, file_path: str):
        """Play an audio file on a speaker."""
        try:
            # Read audio file
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            # Encode audio data to base64 for transmission
            base64_audio = base64.b64encode(audio_data).decode()
            
            # Send command to play audio
            result = await self.client.execute_command(
                device_id=device_id,
                command="play_audio",
                params={"base64_data": base64_audio}
            )
            
            logger.info(f"Played audio file on {device_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
            return {"status": "error", "message": str(e)}

    async def monitor_speakers(self, interval: int = 60):
        """Monitor speakers and play a test tone periodically."""
        while True:
            try:
                # List speakers
                speakers = await self.list_speakers()
                
                if speakers:
                    logger.info(f"Monitoring {len(speakers)} speakers")
                    
                    # Play test tone on each speaker
                    for speaker in speakers:
                        device_id = speaker.get('device_id')
                        name = speaker.get('metadata', {}).get('name', 'Unknown')
                        
                        logger.info(f"Testing speaker: {name} (ID: {device_id})")
                        await self.play_test_tone(
                            device_id=device_id,
                            frequency=440.0,
                            duration=1.0
                        )
                        
                        # Wait for audio to finish
                        await asyncio.sleep(1.5)
                else:
                    logger.warning("No speakers found for monitoring")
                
                # Wait for the next interval
                logger.info(f"Waiting {interval} seconds before next check")
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                await asyncio.sleep(10)  # Wait a bit before retrying


async def main():
    """Run the speaker client."""
    parser = argparse.ArgumentParser(description="UnitAPI Speaker Client")
    parser.add_argument("--host", required=True, help="Speaker agent host")
    parser.add_argument("--port", type=int, default=7890, help="Speaker agent port")
    parser.add_argument("--list", action="store_true", help="List speakers")
    parser.add_argument("--test", action="store_true", help="Test all speakers")
    parser.add_argument("--device", help="Test specific device ID")
    parser.add_argument("--frequency", type=float, default=440.0, help="Test tone frequency in Hz")
    parser.add_argument("--duration", type=float, default=3.0, help="Test tone duration in seconds")
    parser.add_argument("--file", help="Audio file to play")
    parser.add_argument("--monitor", action="store_true", help="Monitor speakers")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    # Create speaker client
    client = SpeakerClient(
        server_host=args.host,
        server_port=args.port
    )
    
    # List speakers
    speakers = await client.list_speakers()
    
    if args.list or not (args.test or args.device or args.file or args.monitor):
        print("\n=== Available Speakers ===")
        for i, speaker in enumerate(speakers):
            print(f"{i+1}. {speaker.get('metadata', {}).get('name', 'Unknown')}")
            print(f"   ID: {speaker.get('device_id')}")
            print(f"   Location: {speaker.get('metadata', {}).get('location', 'Unknown')}")
            print()
    
    # Test specific device
    if args.device:
        if args.file:
            # Play audio file
            await client.play_audio_file(
                device_id=args.device,
                file_path=args.file
            )
        else:
            # Play test tone
            await client.play_test_tone(
                device_id=args.device,
                frequency=args.frequency,
                duration=args.duration
            )
    
    # Test all speakers
    elif args.test and speakers:
        for speaker in speakers:
            device_id = speaker.get('device_id')
            name = speaker.get('metadata', {}).get('name', 'Unknown')
            
            print(f"Testing speaker: {name} (ID: {device_id})")
            await client.play_test_tone(
                device_id=device_id,
                frequency=args.frequency,
                duration=args.duration
            )
            
            # Wait for audio to finish
            await asyncio.sleep(args.duration + 0.5)
    
    # Play audio file on all speakers
    elif args.file and speakers:
        for speaker in speakers:
            device_id = speaker.get('device_id')
            name = speaker.get('metadata', {}).get('name', 'Unknown')
            
            print(f"Playing audio file on speaker: {name} (ID: {device_id})")
            await client.play_audio_file(
                device_id=device_id,
                file_path=args.file
            )
            
            # Wait for audio to finish (assuming 10 seconds for audio file)
            await asyncio.sleep(10)
    
    # Monitor speakers
    elif args.monitor:
        print(f"Monitoring speakers on {args.host}:{args.port}")
        print(f"Interval: {args.interval} seconds")
        print("Press Ctrl+C to stop")
        await client.monitor_speakers(interval=args.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSpeaker client stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
