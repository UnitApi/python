#!/bin/bash
# Test Script for UnitAPI Speaker Agent
# This script tests the UnitAPI speaker agent locally before deploying to a remote machine.
# Usage: ./test_speaker_agent.sh

set -e  # Exit on error

echo "=== UnitAPI Speaker Agent Local Test ==="
echo "This script will test the UnitAPI speaker agent locally."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 before running this test."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed."
    echo "Please install pip3 before running this test."
    exit 1
fi

# Check if PyAudio is installed
echo "=== Checking PyAudio installation ==="
if python3 -c "import pyaudio" &> /dev/null; then
    echo "PyAudio is installed."
else
    echo "PyAudio is not installed."
    echo "Would you like to install PyAudio now? (y/n)"
    read -r install_pyaudio
    if [[ "$install_pyaudio" == "y" ]]; then
        echo "Installing PyAudio..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            sudo apt-get update
            sudo apt-get install -y python3-pyaudio portaudio19-dev
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            brew install portaudio
            pip3 install pyaudio
        else
            # Other OS
            pip3 install pyaudio
        fi
    else
        echo "Skipping PyAudio installation. Some tests may fail."
    fi
fi

# Create a temporary directory for testing
TEMP_DIR=$(mktemp -d)
echo "=== Created temporary directory: $TEMP_DIR ==="

# Create a simple test script
cat > "$TEMP_DIR/test_speakers.py" << 'EOF'
#!/usr/bin/env python3
"""
UnitAPI Speaker Test Script

This script tests the speakers on the local machine.
"""

import asyncio
import argparse
import logging
import sys
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SpeakerTest")

class SpeakerTest:
    """Test speakers on the local machine."""

    async def list_speakers(self):
        """List all available speakers."""
        speakers = []
        
        try:
            # Try to use PyAudio to detect speakers
            import pyaudio
            
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            # Iterate through all audio devices
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                
                # Check if this is an output device (speaker)
                if device_info.get('maxOutputChannels') > 0:
                    device_name = device_info.get('name')
                    channels = device_info.get('maxOutputChannels')
                    sample_rate = int(device_info.get('defaultSampleRate'))
                    
                    # Create device info
                    speaker_info = {
                        'index': i,
                        'name': device_name,
                        'channels': channels,
                        'sample_rate': sample_rate
                    }
                    
                    speakers.append(speaker_info)
                    logger.info(f"Found speaker: {device_name} (index: {i}, channels: {channels}, sample rate: {sample_rate})")
            
            # Clean up
            p.terminate()
                    
        except ImportError:
            logger.warning("PyAudio not available for speaker detection")
            
        # If no speakers found, create a virtual speaker entry
        if not speakers:
            logger.warning("No speakers detected, will use default system audio output")
            speakers.append({
                'index': 0,
                'name': 'Default System Audio',
                'channels': 2,
                'sample_rate': 44100
            })
            
        return speakers

    async def play_test_tone(self, device_index=None, frequency=440.0, duration=3.0, volume=0.5):
        """Play a test tone on a speaker."""
        try:
            import pyaudio
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # If no device index specified, use default output device
            if device_index is None:
                device_index = p.get_default_output_device_info()['index']
                logger.info(f"Using default output device (index: {device_index})")
            
            # Get device info
            device_info = p.get_device_info_by_index(device_index)
            device_name = device_info.get('name')
            channels = min(2, device_info.get('maxOutputChannels'))
            sample_rate = int(device_info.get('defaultSampleRate'))
            
            logger.info(f"Playing {frequency}Hz tone for {duration}s on {device_name}")
            
            # Generate a sine wave tone
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = volume * np.sin(2 * np.pi * frequency * t)
            
            # Apply fade in/out to avoid clicks
            fade_duration = min(0.1, duration / 10)
            fade_samples = int(fade_duration * sample_rate)
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            tone[:fade_samples] *= fade_in
            tone[-fade_samples:] *= fade_out
            
            # Convert to float32 and duplicate for stereo if needed
            audio_data = tone.astype(np.float32)
            if channels == 2:
                audio_data = np.column_stack((audio_data, audio_data))
            
            # Open stream
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Play the tone
            stream.write(audio_data.tobytes())
            
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            logger.info("Audio playback completed")
            return True
            
        except ImportError:
            logger.error("PyAudio not available for audio playback")
            return False
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            return False


async def main():
    """Run the speaker test."""
    parser = argparse.ArgumentParser(description="UnitAPI Speaker Test")
    parser.add_argument("--list", action="store_true", help="List available speakers")
    parser.add_argument("--test", action="store_true", help="Test all speakers")
    parser.add_argument("--device", type=int, help="Test specific device index")
    parser.add_argument("--frequency", type=float, default=440.0, help="Test tone frequency in Hz")
    parser.add_argument("--duration", type=float, default=3.0, help="Test tone duration in seconds")
    parser.add_argument("--volume", type=float, default=0.5, help="Test tone volume (0.0 to 1.0)")
    
    args = parser.parse_args()
    
    # Create speaker test
    test = SpeakerTest()
    
    # List speakers
    speakers = await test.list_speakers()
    
    if args.list or not (args.test or args.device is not None):
        print("\n=== Available Speakers ===")
        for i, speaker in enumerate(speakers):
            print(f"{i+1}. {speaker['name']}")
            print(f"   Index: {speaker['index']}")
            print(f"   Channels: {speaker['channels']}")
            print(f"   Sample Rate: {speaker['sample_rate']}")
            print()
    
    # Test specific device
    if args.device is not None:
        await test.play_test_tone(
            device_index=args.device,
            frequency=args.frequency,
            duration=args.duration,
            volume=args.volume
        )
    
    # Test all speakers
    elif args.test and speakers:
        for speaker in speakers:
            device_index = speaker['index']
            name = speaker['name']
            
            print(f"Testing speaker: {name} (index: {device_index})")
            await test.play_test_tone(
                device_index=device_index,
                frequency=args.frequency,
                duration=args.duration,
                volume=args.volume
            )
            
            # Wait for audio to finish
            await asyncio.sleep(args.duration + 0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
EOF

# Make the test script executable
chmod +x "$TEMP_DIR/test_speakers.py"

# Run the test script to list speakers
echo "=== Testing speaker detection ==="
python3 "$TEMP_DIR/test_speakers.py" --list

# Ask if the user wants to test the speakers
echo ""
echo "Would you like to test the speakers? (y/n)"
read -r test_speakers
if [[ "$test_speakers" == "y" ]]; then
    echo "Testing all speakers..."
    python3 "$TEMP_DIR/test_speakers.py" --test
fi

# Clean up
echo "=== Cleaning up ==="
rm -rf "$TEMP_DIR"

echo ""
echo "=== Test Complete ==="
echo "If the test was successful, you can proceed with installing the UnitAPI Speaker Agent"
echo "on a remote machine using the following command:"
echo ""
echo "  scripts/install_remote_speaker_agent_via_ssh.sh <remote_host> [remote_user]"
echo ""
echo "For more information, see: scripts/REMOTE_SPEAKER_AGENT.md"
echo ""
