#!/bin/bash
# Remote Speaker Agent Installation Script
# This script installs and configures the UnitAPI speaker agent on a remote machine
# Usage: ./install_remote_speaker_agent.sh

set -e  # Exit on error

echo "=== UnitAPI Remote Speaker Agent Installation ==="
echo "This script will install and configure the UnitAPI speaker agent"
echo "to manage hardware and prepare the server for all speakers."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Cannot detect OS, assuming Debian/Ubuntu compatible"
    OS="Unknown"
    VER="Unknown"
fi

echo "Detected OS: $OS $VER"

# Install system dependencies
echo "=== Installing system dependencies ==="
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git portaudio19-dev python3-pyaudio
elif [[ "$OS" == *"Fedora"* ]] || [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    dnf install -y python3 python3-pip python3-virtualenv git portaudio-devel
    dnf install -y python3-pyaudio || echo "PyAudio not available in repos, will install via pip"
elif [[ "$OS" == *"Arch"* ]]; then
    pacman -Sy --noconfirm python python-pip python-virtualenv git portaudio
    pacman -Sy --noconfirm python-pyaudio || echo "PyAudio not available in repos, will install via pip"
else
    echo "Unsupported OS: $OS. Installing basic dependencies."
    # Try generic commands that might work on other Linux distros
    command -v apt-get && apt-get update && apt-get install -y python3 python3-pip git portaudio19-dev
    command -v dnf && dnf install -y python3 python3-pip git portaudio-devel
    command -v pacman && pacman -Sy --noconfirm python python-pip git portaudio
fi

# Create installation directory
INSTALL_DIR="/opt/unitapi"
echo "=== Creating installation directory at $INSTALL_DIR ==="
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Create virtual environment
echo "=== Setting up Python virtual environment ==="
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install wheel setuptools
pip install pyaudio websockets numpy sounddevice soundfile

# Clone UnitAPI repository
echo "=== Cloning UnitAPI repository ==="
if [ -d "UnitApi" ]; then
    echo "UnitApi directory already exists, updating..."
    cd UnitApi
    git pull
    cd ..
else
    git clone https://github.com/UnitApi/python.git
    cd UnitApi
    cd ..
fi

# Install UnitAPI
echo "=== Installing UnitAPI ==="
cd UnitApi/python
pip install -e .
cd ../..

# Create speaker agent service files
echo "=== Creating speaker agent service ==="

# Create the speaker agent script
cat > $INSTALL_DIR/speaker_agent.py << 'EOF'
#!/usr/bin/env python3
"""
UnitAPI Remote Speaker Agent

This script runs a server that manages all speakers on the system and makes them
available for remote control via the UnitAPI protocol.
"""

import asyncio
import logging
import argparse
import os
import sys
import json
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/unitapi_speaker_agent.log')
    ]
)
logger = logging.getLogger("SpeakerAgent")

# Import UnitAPI modules
try:
    from unitapi.core.server import UnitAPIServer
    from unitapi.protocols.websocket import WebSocketProtocol
    from unitapi.devices.remote_speaker_device import RemoteSpeakerDevice, generate_test_audio
except ImportError:
    logger.error("UnitAPI modules not found. Please install UnitAPI.")
    sys.exit(1)

# Import PyAudio for speaker detection
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    logger.warning("PyAudio not available. Limited speaker functionality.")
    PYAUDIO_AVAILABLE = False


class SpeakerAgent:
    """UnitAPI Speaker Agent for managing all system speakers."""

    def __init__(
            self,
            server_host: str = '0.0.0.0',
            server_port: int = 7890,
            ws_host: str = '0.0.0.0',
            ws_port: int = 8765,
            config_file: str = '/etc/unitapi/speaker_agent.json'
    ):
        """Initialize the speaker agent."""
        self.server_host = server_host
        self.server_port = server_port
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.config_file = config_file
        
        # UnitAPI Server
        self.server = UnitAPIServer(host=server_host, port=server_port)
        
        # WebSocket Protocol
        self.websocket = WebSocketProtocol(host=ws_host, port=ws_port)
        
        # Speakers registry
        self.speakers = {}
        
        # Configuration
        self.config = self._load_config()
        
        logger.info(f"Speaker Agent initialized on {server_host}:{server_port}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        default_config = {
            "auto_register_speakers": True,
            "speakers": []
        }
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Save default config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
        
        return default_config

    def _save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    async def detect_speakers(self) -> List[Dict[str, Any]]:
        """Detect all speakers on the system."""
        speakers = []
        
        if not PYAUDIO_AVAILABLE:
            logger.warning("PyAudio not available for speaker detection")
            # Add a default speaker
            speakers.append({
                "device_id": "default_speaker",
                "name": "Default System Speaker",
                "location": "System",
                "index": 0,
                "channels": 2,
                "sample_rate": 44100
            })
            return speakers
        
        try:
            # Use PyAudio to detect speakers
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
                        "device_id": f"speaker_{i}",
                        "name": device_name,
                        "location": "System",
                        "index": i,
                        "channels": channels,
                        "sample_rate": sample_rate
                    }
                    
                    speakers.append(speaker_info)
                    logger.info(f"Found speaker: {device_name} (index: {i}, channels: {channels}, sample rate: {sample_rate})")
            
            # Clean up
            p.terminate()
                    
        except Exception as e:
            logger.error(f"Error detecting speakers: {e}")
        
        # If no speakers found, add a default one
        if not speakers:
            logger.warning("No speakers detected, adding default system audio output")
            speakers.append({
                "device_id": "default_speaker",
                "name": "Default System Speaker",
                "location": "System",
                "index": 0,
                "channels": 2,
                "sample_rate": 44100
            })
            
        return speakers

    async def register_speaker(self, speaker_info: Dict[str, Any]) -> bool:
        """Register a speaker with the UnitAPI server."""
        try:
            device_id = speaker_info["device_id"]
            name = speaker_info["name"]
            location = speaker_info.get("location", "System")
            index = speaker_info.get("index", 0)
            channels = speaker_info.get("channels", 2)
            sample_rate = speaker_info.get("sample_rate", 44100)
            
            # Create speaker device
            speaker = RemoteSpeakerDevice(
                device_id=device_id,
                name=name,
                metadata={
                    "location": location,
                    "index": index,
                    "channels": channels,
                    "sample_rate": sample_rate
                }
            )
            
            # Connect speaker
            await speaker.connect()
            
            # Register in server
            self.server.register_device(
                device_id=device_id,
                device_type="speaker",
                metadata={
                    "name": name,
                    "location": location,
                    "index": index,
                    "channels": channels,
                    "sample_rate": sample_rate
                }
            )
            
            # Store in registry
            self.speakers[device_id] = speaker
            
            logger.info(f"Registered speaker: {name} (ID: {device_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering speaker: {e}")
            return False

    async def register_all_speakers(self) -> None:
        """Register all detected speakers."""
        # Detect speakers
        detected_speakers = await self.detect_speakers()
        
        # Register each speaker
        for speaker_info in detected_speakers:
            await self.register_speaker(speaker_info)
            
        # Update config with detected speakers
        if self.config["auto_register_speakers"]:
            self.config["speakers"] = detected_speakers
            self._save_config()

    async def start(self) -> None:
        """Start the speaker agent."""
        logger.info("Starting Speaker Agent")
        
        # Register speakers from config
        if self.config["speakers"] and not self.config["auto_register_speakers"]:
            for speaker_info in self.config["speakers"]:
                await self.register_speaker(speaker_info)
        else:
            # Auto-detect and register speakers
            await self.register_all_speakers()
        
        # Start UnitAPI server
        server_task = asyncio.create_task(self.server.start())
        
        # Start WebSocket server
        websocket_task = asyncio.create_task(self.websocket.create_server())
        
        logger.info(f"Speaker Agent running on {self.server_host}:{self.server_port}")
        logger.info(f"WebSocket server running on {self.ws_host}:{self.ws_port}")
        
        # Wait for servers to run
        await asyncio.gather(server_task, websocket_task)

    async def test_speakers(self) -> None:
        """Test all registered speakers by playing a tone."""
        logger.info("Testing all registered speakers")
        
        for device_id, speaker in self.speakers.items():
            try:
                # Generate test audio
                test_audio = generate_test_audio(
                    duration=2.0,
                    frequency=440.0,  # A4 note
                    sample_rate=speaker.sample_rate
                )
                
                # Play test audio
                logger.info(f"Testing speaker: {speaker.name} (ID: {device_id})")
                await speaker.play_audio(test_audio)
                
                # Wait for audio to finish
                await asyncio.sleep(2.5)
                
            except Exception as e:
                logger.error(f"Error testing speaker {device_id}: {e}")


async def main():
    """Run the speaker agent."""
    parser = argparse.ArgumentParser(description="UnitAPI Remote Speaker Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=7890, help="Server port")
    parser.add_argument("--ws-host", default="0.0.0.0", help="WebSocket host")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--config", default="/etc/unitapi/speaker_agent.json", help="Config file path")
    parser.add_argument("--test", action="store_true", help="Test speakers and exit")
    parser.add_argument("--list", action="store_true", help="List speakers and exit")
    
    args = parser.parse_args()
    
    # Create speaker agent
    agent = SpeakerAgent(
        server_host=args.host,
        server_port=args.port,
        ws_host=args.ws_host,
        ws_port=args.ws_port,
        config_file=args.config
    )
    
    if args.list:
        # Just detect and list speakers
        speakers = await agent.detect_speakers()
        print("\n=== Available Speakers ===")
        for i, speaker in enumerate(speakers):
            print(f"{i+1}. {speaker['name']}")
            print(f"   ID: {speaker['device_id']}")
            print(f"   Index: {speaker['index']}")
            print(f"   Channels: {speaker['channels']}")
            print(f"   Sample Rate: {speaker['sample_rate']}")
            print()
        return
    
    if args.test:
        # Register speakers and test them
        await agent.register_all_speakers()
        await agent.test_speakers()
        return
    
    # Start the agent
    await agent.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Speaker Agent stopped by user")
    except Exception as e:
        logger.error(f"Speaker Agent error: {e}")
        sys.exit(1)
EOF

# Make the script executable
chmod +x $INSTALL_DIR/speaker_agent.py

# Create systemd service file
cat > /etc/systemd/system/unitapi-speaker-agent.service << EOF
[Unit]
Description=UnitAPI Speaker Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/speaker_agent.py
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=unitapi-speaker

[Install]
WantedBy=multi-user.target
EOF

# Create configuration directory
mkdir -p /etc/unitapi

# Create default configuration
cat > /etc/unitapi/speaker_agent.json << EOF
{
  "auto_register_speakers": true,
  "speakers": []
}
EOF

# Create a simple client script for testing
cat > $INSTALL_DIR/test_speaker_client.py << 'EOF'
#!/usr/bin/env python3
"""
UnitAPI Speaker Client Test Script

This script tests the connection to a remote UnitAPI speaker agent and plays
a test tone on all available speakers.
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
logger = logging.getLogger("SpeakerClient")

# Import UnitAPI modules
try:
    from unitapi.core.client import UnitAPIClient
except ImportError:
    logger.error("UnitAPI modules not found. Please install UnitAPI.")
    sys.exit(1)


class SpeakerClient:
    """Client for testing UnitAPI speaker agent."""

    def __init__(self, server_host: str, server_port: int = 7890):
        """Initialize the speaker client."""
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )
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
            import base64
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


async def main():
    """Run the speaker client test."""
    parser = argparse.ArgumentParser(description="UnitAPI Speaker Client Test")
    parser.add_argument("--host", required=True, help="Speaker agent host")
    parser.add_argument("--port", type=int, default=7890, help="Speaker agent port")
    parser.add_argument("--list", action="store_true", help="List speakers")
    parser.add_argument("--test", action="store_true", help="Test all speakers")
    parser.add_argument("--device", help="Test specific device ID")
    parser.add_argument("--frequency", type=float, default=440.0, help="Test tone frequency in Hz")
    parser.add_argument("--duration", type=float, default=3.0, help="Test tone duration in seconds")
    
    args = parser.parse_args()
    
    # Create speaker client
    client = SpeakerClient(
        server_host=args.host,
        server_port=args.port
    )
    
    # List speakers
    speakers = await client.list_speakers()
    
    if args.list or not (args.test or args.device):
        print("\n=== Available Speakers ===")
        for i, speaker in enumerate(speakers):
            print(f"{i+1}. {speaker.get('metadata', {}).get('name', 'Unknown')}")
            print(f"   ID: {speaker.get('device_id')}")
            print(f"   Location: {speaker.get('metadata', {}).get('location', 'Unknown')}")
            print()
    
    # Test specific device
    if args.device:
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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
EOF

# Make the client script executable
chmod +x $INSTALL_DIR/test_speaker_client.py

# Create a simple wrapper script for SSH usage
cat > $INSTALL_DIR/remote_speaker_setup.sh << 'EOF'
#!/bin/bash
# UnitAPI Remote Speaker Setup Script

# Display help
show_help() {
    echo "UnitAPI Remote Speaker Setup Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --list          List all available speakers"
    echo "  --test          Test all speakers"
    echo "  --start         Start the speaker agent service"
    echo "  --stop          Stop the speaker agent service"
    echo "  --status        Check the speaker agent service status"
    echo "  --enable        Enable the speaker agent service at boot"
    echo "  --disable       Disable the speaker agent service at boot"
    echo "  --help          Show this help message"
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Process arguments
case "$1" in
    --list)
        echo "Listing available speakers..."
        /opt/unitapi/venv/bin/python /opt/unitapi/speaker_agent.py --list
        ;;
    --test)
        echo "Testing all speakers..."
        /opt/unitapi/venv/bin/python /opt/unitapi/speaker_agent.py --test
        ;;
    --start)
        echo "Starting speaker agent service..."
        systemctl start unitapi-speaker-agent
        systemctl status unitapi-speaker-agent
        ;;
    --stop)
        echo "Stopping speaker agent service..."
        systemctl stop unitapi-speaker-agent
        ;;
    --status)
        echo "Speaker agent service status:"
        systemctl status unitapi-speaker-agent
        ;;
    --enable)
        echo "Enabling speaker agent service at boot..."
        systemctl enable unitapi-speaker-agent
        ;;
    --disable)
        echo "Disabling speaker agent service at boot..."
        systemctl disable unitapi-speaker-agent
        ;;
    --help)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
EOF

# Make the wrapper script executable
chmod +x $INSTALL_DIR/remote_speaker_setup.sh

# Create a symlink to make it easier to access
ln -sf $INSTALL_DIR/remote_speaker_setup.sh /usr/local/bin/unitapi-speaker

# Enable and start the service
echo "=== Enabling and starting the UnitAPI Speaker Agent service ==="
systemctl daemon-reload
systemctl enable unitapi-speaker-agent
systemctl start unitapi-speaker-agent

# Test the installation
echo "=== Testing the installation ==="
$INSTALL_DIR/remote_speaker_setup.sh --list

echo ""
echo "=== Installation Complete ==="
echo "The UnitAPI Speaker Agent has been installed and configured."
echo ""
echo "You can manage the speaker agent using the following commands:"
echo "  unitapi-speaker --list    : List all available speakers"
echo "  unitapi-speaker --test    : Test all speakers"
echo "  unitapi-speaker --status  : Check the service status"
echo "  unitapi-speaker --stop    : Stop the service"
echo "  unitapi-speaker --start   : Start the service"
echo ""
echo "To connect to this speaker agent from another machine:"
echo "  python test_speaker_client.py --host <this-machine-ip> --list"
echo ""
