# Remote Keyboard Server Installation Guide

This document provides information about installing and configuring the UnitAPI Remote Keyboard Server on a Raspberry Pi.

## Overview

The Remote Keyboard Server allows you to control a Raspberry Pi's keyboard remotely using the UnitAPI framework. This enables you to send keystrokes to the Raspberry Pi from another computer, which can be useful for remote control, automation, and testing scenarios.

## Installation Options

There are two installation scripts available:

1. **Standard Installation Script**: `scripts/install_remote_keyboard_server.sh`
2. **Fixed Installation Script**: `scripts/install_remote_keyboard_server_fixed.sh` (Recommended)

The fixed installation script includes several improvements to handle common installation issues.

## Improvements in the Fixed Installation Script

The `install_remote_keyboard_server_fixed.sh` script includes the following improvements:

1. **Improved SSH Authentication**:
   - Explicitly disables pubkey authentication when using password authentication to prevent "too many authentication failures" errors
   - Adds retry mechanism for SSH connections with configurable number of attempts
   - Provides better error messages for authentication failures

2. **Repository Handling**:
   - Detects outdated Raspberry Pi OS versions (like "stretch")
   - Updates repository sources to use archive repositories for outdated OS versions
   - Prevents 404 errors when accessing outdated repositories

3. **SSL Certificate Verification**:
   - Disables SSL certificate verification for pip installations using `--trusted-host` flags
   - Resolves SSL certificate verification failures when installing Python packages
   - Adds trusted hosts for both PyPI and piwheels repositories

4. **Improved File Transfer**:
   - Adds retry mechanism for SCP file transfers
   - Verifies successful file transfers before proceeding
   - Creates a local service file and transfers it directly to avoid path issues

5. **Error Handling and Recovery**:
   - Adds retry mechanisms for package installation and unitapi installation
   - Continues installation even if some steps fail, with appropriate warnings
   - Provides more detailed error messages and status updates

## Usage

### Basic Installation

```bash
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry
```

### Using SSH Key Authentication

```bash
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --identity ~/.ssh/id_rsa
```

### Controlling the Service

```bash
# Start the service
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry --service-command start

# Stop the service
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry --service-command stop

# Restart the service
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry --service-command restart

# Check service status
./scripts/install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry --service-command status
```

## Client Configuration

After installing the Remote Keyboard Server on your Raspberry Pi, you need to configure the client to connect to it.

1. Update your `.env` file with the following:

```
RPI_HOST=192.168.1.100  # Replace with your Raspberry Pi's IP address
RPI_USER=pi             # Replace with your Raspberry Pi username
RPI_PASSWORD=raspberry  # Replace with your Raspberry Pi password
```

2. Run the client:

```bash
python examples/remote_keyboard_control_fixed.py
```

> **Note:** We recommend using the fixed version of the client script (`remote_keyboard_control_fixed.py`) instead of the original version (`remote_keyboard_control.py`). The fixed version includes better error handling, connection checking, and troubleshooting guidance.

### Client Script Options

The remote keyboard control client supports several command-line options:

```bash
python examples/remote_keyboard_control_fixed.py --help
```

Common options include:

- `--check-connection`: Test the connection to the remote server
- `--list`: List available keyboards on the remote device
- `--device-id DEVICE_ID`: Specify a keyboard device ID to control
- `--text TEXT`: Type the specified text on the remote keyboard
- `--key KEY`: Press a specific key on the remote keyboard
- `--hotkey KEYS`: Press a hotkey combination (comma-separated keys, e.g., ctrl,s)

## Troubleshooting

### SSH Connection Issues

If you're experiencing SSH connection issues:

1. Verify that the Raspberry Pi is reachable on the network:
   ```bash
   ping <raspberry_pi_ip>
   ```

2. Check that SSH is enabled on the Raspberry Pi:
   ```bash
   ssh <username>@<raspberry_pi_ip>
   ```

3. If using password authentication, ensure the password is correct.

4. If using key-based authentication, ensure the key file exists and has the correct permissions:
   ```bash
   chmod 600 ~/.ssh/id_rsa
   ```

### Package Installation Issues

If package installation fails:

1. Check the Raspberry Pi's internet connection.

2. Try updating the package lists manually:
   ```bash
   sudo apt-get update
   ```

3. If using an outdated Raspberry Pi OS version, consider upgrading to a newer version.

### Service Issues

If the service fails to start:

1. Check the service status:
   ```bash
   sudo systemctl status unitapi-keyboard.service
   ```

2. Check the service logs:
   ```bash
   journalctl -u unitapi-keyboard.service
   ```

3. Verify that the Python virtual environment was created correctly:
   ```bash
   ls -la /home/pi/unitapi/venv/bin/python
   ```

## Python Installation Alternative

If you prefer using Python instead of Bash for installation, you can use the `scripts/install_remote_keyboard_server.py` script:

```bash
python scripts/install_remote_keyboard_server.py --host 192.168.1.100 --password raspberry
```

This Python script provides similar functionality to the Bash script but may be more suitable for environments where Python is preferred over Bash.
