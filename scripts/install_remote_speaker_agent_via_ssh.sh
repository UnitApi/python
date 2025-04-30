#!/bin/bash
# Remote Speaker Agent Installation via SSH
# This script connects to a remote PC via SSH, transfers the installation script,
# and executes it to set up the UnitAPI speaker agent.
# Usage: ./install_remote_speaker_agent_via_ssh.sh <remote_host> [remote_user]

set -e  # Exit on error

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <remote_host> [remote_user]"
    echo "Example: $0 192.168.1.100 pi"
    exit 1
fi

REMOTE_HOST="$1"
REMOTE_USER="${2:-root}"  # Default to root if not specified

echo "=== UnitAPI Remote Speaker Agent Installation via SSH ==="
echo "This script will connect to $REMOTE_USER@$REMOTE_HOST and install the UnitAPI speaker agent."

# Check if the installation script exists
INSTALL_SCRIPT="scripts/install_remote_speaker_agent.sh"
if [ ! -f "$INSTALL_SCRIPT" ]; then
    echo "Error: Installation script not found at $INSTALL_SCRIPT"
    exit 1
fi

# Make sure the installation script is executable
chmod +x "$INSTALL_SCRIPT"

# Check SSH connection
echo "=== Testing SSH connection to $REMOTE_USER@$REMOTE_HOST ==="
ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" echo "SSH connection successful" || {
    echo "Error: Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    echo "Please make sure:"
    echo "1. The remote host is reachable"
    echo "2. SSH is enabled on the remote host"
    echo "3. You have the correct credentials"
    echo "4. You have SSH key-based authentication set up or can provide a password"
    exit 1
}

# Create a temporary directory on the remote host
echo "=== Creating temporary directory on remote host ==="
REMOTE_TEMP_DIR=$(ssh "$REMOTE_USER@$REMOTE_HOST" "mktemp -d")
echo "Created temporary directory: $REMOTE_TEMP_DIR"

# Copy the installation script to the remote host
echo "=== Copying installation script to remote host ==="
scp "$INSTALL_SCRIPT" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_TEMP_DIR/install_remote_speaker_agent.sh"

# Make the script executable on the remote host
ssh "$REMOTE_USER@$REMOTE_HOST" "chmod +x $REMOTE_TEMP_DIR/install_remote_speaker_agent.sh"

# Execute the installation script on the remote host
echo "=== Executing installation script on remote host ==="
echo "This may take a few minutes..."
ssh -t "$REMOTE_USER@$REMOTE_HOST" "sudo $REMOTE_TEMP_DIR/install_remote_speaker_agent.sh"

# Clean up the temporary directory
echo "=== Cleaning up temporary directory ==="
ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $REMOTE_TEMP_DIR"

echo ""
echo "=== Remote Installation Complete ==="
echo "The UnitAPI Speaker Agent has been installed on $REMOTE_HOST."
echo ""
echo "You can manage the speaker agent on the remote machine using:"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'sudo unitapi-speaker --list'    : List all available speakers"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'sudo unitapi-speaker --test'    : Test all speakers"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'sudo unitapi-speaker --status'  : Check the service status"
echo ""
echo "To connect to the remote speaker agent from this machine:"
echo "  1. Install UnitAPI on this machine"
echo "  2. Run: python test_speaker_client.py --host $REMOTE_HOST --list"
echo ""

# Create a simple client script for testing the remote speakers
echo "=== Creating local client script for testing remote speakers ==="
cat > remote_speaker_client.py << 'EOF'
#!/usr/bin/env python3
"""
UnitAPI Remote Speaker Client

This script connects to a remote UnitAPI speaker agent and allows you to
list and test speakers on the remote machine.
"""

import asyncio
import argparse
import logging
import sys
import numpy as np
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RemoteSpeakerClient")

# Check if UnitAPI is installed
try:
    from unitapi.core.client import UnitAPIClient
except ImportError:
    logger.error("UnitAPI not found. Please install UnitAPI first.")
    logger.error("You can install it with: pip install unitapi")
    sys.exit(1)


class RemoteSpeakerClient:
    """Client for controlling remote UnitAPI speakers."""

    def __init__(self, server_host: str, server_port: int = 7890):
        """Initialize the remote speaker client."""
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )
        logger.info(f"Connected to remote speaker agent at {server_host}:{server_port}")

    async def list_speakers(self):
        """List all available speakers on the remote machine."""
        try:
            # Get list of speakers from server
            speakers = await self.client.list_devices(device_type="speaker")
            
            if not speakers:
                logger.warning("No speakers found on the remote machine")
                return []
                
            logger.info(f"Found {len(speakers)} speakers on the remote machine")
            return speakers
            
        except Exception as e:
            logger.error(f"Error listing speakers: {e}")
            return []

    async def play_test_tone(self, device_id: str, frequency: float = 440.0, duration: float = 3.0):
        """Play a test tone on a remote speaker."""
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
            
            logger.info(f"Played test tone on remote speaker {device_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error playing test tone: {e}")
            return {"status": "error", "message": str(e)}

    async def play_audio_file(self, device_id: str, file_path: str):
        """Play an audio file on a remote speaker."""
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
            
            logger.info(f"Played audio file on remote speaker {device_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
            return {"status": "error", "message": str(e)}


async def main():
    """Run the remote speaker client."""
    parser = argparse.ArgumentParser(description="UnitAPI Remote Speaker Client")
    parser.add_argument("--host", required=True, help="Remote speaker agent host")
    parser.add_argument("--port", type=int, default=7890, help="Remote speaker agent port")
    parser.add_argument("--list", action="store_true", help="List remote speakers")
    parser.add_argument("--test", action="store_true", help="Test all remote speakers")
    parser.add_argument("--device", help="Test specific remote speaker device ID")
    parser.add_argument("--frequency", type=float, default=440.0, help="Test tone frequency in Hz")
    parser.add_argument("--duration", type=float, default=3.0, help="Test tone duration in seconds")
    parser.add_argument("--file", help="Audio file to play on remote speaker")
    
    args = parser.parse_args()
    
    # Create remote speaker client
    client = RemoteSpeakerClient(
        server_host=args.host,
        server_port=args.port
    )
    
    # List speakers
    speakers = await client.list_speakers()
    
    if args.list or not (args.test or args.device or args.file):
        print("\n=== Available Remote Speakers ===")
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
            
            print(f"Testing remote speaker: {name} (ID: {device_id})")
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
            
            print(f"Playing audio file on remote speaker: {name} (ID: {device_id})")
            await client.play_audio_file(
                device_id=device_id,
                file_path=args.file
            )
            
            # Wait for audio to finish (assuming 10 seconds for audio file)
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nRemote speaker client stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
EOF

chmod +x remote_speaker_client.py

echo "Created local client script: remote_speaker_client.py"
echo "You can use it to test the remote speakers:"
echo "  python remote_speaker_client.py --host $REMOTE_HOST --list"
echo "  python remote_speaker_client.py --host $REMOTE_HOST --test"
echo "  python remote_speaker_client.py --host $REMOTE_HOST --device <device_id> --file <audio_file>"
