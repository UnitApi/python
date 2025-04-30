# UnitAPI Installation Guide

## Prerequisites

- Python 3.8+
- pip package manager

## Installation Methods

### 1. pip Installation (Recommended)

```bash
pip install unitapi
```

### 2. Optional Protocol Support

```bash
# Install with MQTT support
pip install unitapi[mqtt]

# Install with WebSocket support
pip install unitapi[websocket]
```

### 3. From Source

```bash
# Clone the repository
git clone https://github.com/yourUnitApi/python.git
cd unitapi

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install .
```

## Verification

To verify the installation, run:

```bash
python -c "import unitapi; print(unitapi.__version__)"
```

## Dependencies

### Core Dependencies
- `asyncio`
- `pydantic`
- `cryptography`
- `python-jose`

### Optional Dependencies
- `paho-mqtt` (for MQTT support)
- `websockets` (for WebSocket support)
- `pyaudio` (for audio device support)
- `opencv-python` (for camera support)

## Troubleshooting

### Common Installation Issues

1. **Python Version Compatibility**
   - Ensure you're using Python 3.8 or newer
   - Use `python3 -m pip install unitapi` if multiple Python versions are installed

2. **Permission Issues**
   - On Unix-like systems, use `sudo pip install unitapi` 
   - Recommended: Use virtual environments

3. **Dependency Conflicts**
   - Create a virtual environment before installation
   ```bash
   python3 -m venv unitapi_env
   source unitapi_env/bin/activate  # On Windows: unitapi_env\Scripts\activate
   pip install unitapi
   ```

4. **PyAudio Installation Issues**
   - On Linux, you may need to install PortAudio development headers:
   ```bash
   sudo apt-get install portaudio19-dev
   pip install pyaudio
   ```
   - On macOS, you can use Homebrew:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```
   - On Windows, you might need to install a pre-built wheel:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

## Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/yourUnitApi/python.git
cd unitapi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Activate virtual environment

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .
```

## System-Specific Notes

### Raspberry Pi
- Ensure `python3-dev` package is installed
```bash
sudo apt-get update
sudo apt-get install python3-dev
pip install unitapi
```

### Docker
```dockerfile
FROM python:3.9-slim

# Install UnitAPI
RUN pip install unitapi

# Optional: Install additional protocol support
RUN pip install unitapi[mqtt,websocket]
```

## Updating UnitAPI

```bash
# Upgrade to latest version
pip install --upgrade unitapi

# Upgrade with specific protocol support
pip install --upgrade unitapi[mqtt]
```

## Uninstallation

```bash
pip uninstall unitapi
```

## Remote Speaker Agent Installation

For installing the Remote Speaker Agent on a remote machine, see the [Remote Speaker Agent documentation](remote_speaker_agent.md).

### Quick Remote Installation

```bash
# Install on a remote machine via SSH
scripts/install_remote_speaker_agent_via_ssh.sh remote-host [remote-user]

# Example:
scripts/install_remote_speaker_agent_via_ssh.sh 192.168.1.100 pi
