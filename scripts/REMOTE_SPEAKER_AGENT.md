# UnitAPI Remote Speaker Agent

This document explains how to install and use the UnitAPI Remote Speaker Agent, which allows you to manage and control speakers on a remote PC via SSH.

## Overview

The UnitAPI Remote Speaker Agent is a service that runs on a remote machine and provides access to all speakers on that machine through the UnitAPI protocol. This allows you to:

- Discover all speakers on the remote machine
- Play audio on specific speakers
- Test speakers with test tones
- Stream audio from one machine to speakers on another

## Installation

Before installing on a remote machine, you can test your local setup to ensure everything works correctly.

### 0. Testing Your Local Setup

You can test your local speaker setup before deploying to a remote machine:

```bash
# Run the local test script
scripts/test_speaker_agent.sh
```

This script will:
1. Check if PyAudio is installed and offer to install it if needed
2. Detect all speakers on your local machine
3. Optionally test all speakers by playing a test tone
4. Provide guidance for proceeding with remote installation

After confirming your local setup works correctly, you can proceed with one of the following installation methods:

There are two ways to install the Remote Speaker Agent:

### 1. Direct Installation on the Remote Machine

If you have direct access to the remote machine, you can install the agent directly:

```bash
# Log in to the remote machine
ssh user@remote-host

# Clone the UnitAPI repository (if not already done)
git clone https://github.com/UnitApi/python.git
cd UnitApi/python

# Run the installation script
sudo scripts/install_remote_speaker_agent.sh
```

### 2. Remote Installation via SSH

If you only have SSH access to the remote machine, you can install the agent remotely from your local machine:

```bash
# Clone the UnitAPI repository (if not already done)
git clone https://github.com/UnitApi/python.git
cd UnitApi/python

# Run the remote installation script
scripts/install_remote_speaker_agent_via_ssh.sh remote-host [remote-user]

# Example:
scripts/install_remote_speaker_agent_via_ssh.sh 192.168.1.100 pi
```

The remote installation script will:
1. Connect to the remote machine via SSH
2. Copy the installation script to the remote machine
3. Execute the installation script on the remote machine
4. Create a local client script for testing the remote speakers

## Managing the Remote Speaker Agent

After installation, you can manage the Remote Speaker Agent on the remote machine using the following commands:

```bash
# List all available speakers
ssh user@remote-host 'sudo unitapi-speaker --list'

# Test all speakers
ssh user@remote-host 'sudo unitapi-speaker --test'

# Check the service status
ssh user@remote-host 'sudo unitapi-speaker --status'

# Start the service
ssh user@remote-host 'sudo unitapi-speaker --start'

# Stop the service
ssh user@remote-host 'sudo unitapi-speaker --stop'

# Enable the service to start at boot
ssh user@remote-host 'sudo unitapi-speaker --enable'

# Disable the service from starting at boot
ssh user@remote-host 'sudo unitapi-speaker --disable'
```

## Connecting to the Remote Speaker Agent

### Using the Local Test Script

Before connecting to a remote speaker agent, you can test your local speakers:

```bash
# Test your local speakers
scripts/test_speaker_agent.sh
```

### Connecting to Remote Speakers

To connect to the Remote Speaker Agent from another machine, you can use the provided client script:

```bash
# If you used the remote installation script, a client script was created for you
python remote_speaker_client.py --host remote-host --list

# List all available speakers
python remote_speaker_client.py --host remote-host --list

# Test all speakers
python remote_speaker_client.py --host remote-host --test

# Test a specific speaker
python remote_speaker_client.py --host remote-host --device speaker_id

# Play an audio file on a specific speaker
python remote_speaker_client.py --host remote-host --device speaker_id --file path/to/audio.wav

# Play a test tone with custom frequency and duration
python remote_speaker_client.py --host remote-host --device speaker_id --frequency 880 --duration 2.0
```

## Technical Details

The Remote Speaker Agent consists of the following components:

1. **UnitAPI Server**: Handles device registration and communication
2. **WebSocket Server**: Provides a WebSocket interface for real-time communication
3. **Speaker Detection**: Automatically detects all speakers on the system
4. **Speaker Registry**: Maintains a registry of all available speakers
5. **Configuration**: Stores speaker configuration in `/etc/unitapi/speaker_agent.json`
6. **Systemd Service**: Runs the agent as a system service (`unitapi-speaker-agent`)

The agent is installed in `/opt/unitapi` and runs in a Python virtual environment to avoid conflicts with system packages.

## Troubleshooting

If you encounter issues with the Remote Speaker Agent, check the following:

1. **Service Status**: Check if the service is running
   ```bash
   ssh user@remote-host 'sudo systemctl status unitapi-speaker-agent'
   ```

2. **Logs**: Check the service logs
   ```bash
   ssh user@remote-host 'sudo journalctl -u unitapi-speaker-agent'
   ```

3. **Configuration**: Check the configuration file
   ```bash
   ssh user@remote-host 'sudo cat /etc/unitapi/speaker_agent.json'
   ```

4. **Network**: Make sure the remote machine is reachable and the required ports are open
   ```bash
   # Test connectivity
   ping remote-host
   
   # Test if the UnitAPI port is open
   nc -zv remote-host 7890
   
   # Test if the WebSocket port is open
   nc -zv remote-host 8765
   ```

5. **Dependencies**: Make sure all required dependencies are installed
   ```bash
   ssh user@remote-host 'sudo /opt/unitapi/venv/bin/pip list | grep -E "pyaudio|websockets|numpy|sounddevice|soundfile"'
   ```

## Advanced Usage

### Custom Configuration

You can customize the Remote Speaker Agent by editing the configuration file:

```bash
ssh user@remote-host 'sudo nano /etc/unitapi/speaker_agent.json'
```

Configuration options:
- `auto_register_speakers`: Whether to automatically register all detected speakers (default: `true`)
- `speakers`: List of manually configured speakers (used when `auto_register_speakers` is `false`)

### Multiple Remote Machines

You can install the Remote Speaker Agent on multiple machines and control them all from a single client:

```bash
# Install on multiple machines
scripts/install_remote_speaker_agent_via_ssh.sh machine1 user1
scripts/install_remote_speaker_agent_via_ssh.sh machine2 user2

# Connect to each machine
python remote_speaker_client.py --host machine1 --list
python remote_speaker_client.py --host machine2 --list

# Play audio on specific speakers on different machines
python remote_speaker_client.py --host machine1 --device speaker_id1 --file audio1.wav
python remote_speaker_client.py --host machine2 --device speaker_id2 --file audio2.wav
```

### Integration with Other UnitAPI Devices

The Remote Speaker Agent can be integrated with other UnitAPI devices, such as microphones, cameras, and sensors, to create a complete IoT system:

```python
from unitapi.core.client import UnitAPIClient

# Connect to multiple UnitAPI servers
speaker_client = UnitAPIClient(server_host="speaker-host", server_port=7890)
microphone_client = UnitAPIClient(server_host="microphone-host", server_port=7890)
camera_client = UnitAPIClient(server_host="camera-host", server_port=7890)

# List devices on each server
speakers = await speaker_client.list_devices(device_type="speaker")
microphones = await microphone_client.list_devices(device_type="microphone")
cameras = await camera_client.list_devices(device_type="camera")

# Create a complete IoT system
# ...
```

## License

The UnitAPI Remote Speaker Agent is part of the UnitAPI project and is licensed under the same license as UnitAPI.
