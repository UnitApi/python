# Remote Keyboard Control

This directory contains scripts for controlling a keyboard on a remote Raspberry Pi device.

## Overview

The Remote Keyboard Control system allows you to send keyboard commands from your computer to a Raspberry Pi over the network. This can be useful for:

- Remote control of Raspberry Pi applications
- Automation of keyboard input for testing
- Controlling devices without direct physical access
- Creating interactive demos and presentations

## Components

The system consists of two main components:

1. **Server** (`remote_keyboard_server.py`): Runs on the Raspberry Pi and registers a keyboard device with the UnitAPI server.
2. **Client** (`remote_keyboard_control_fixed.py`): Runs on your computer and sends keyboard commands to the server.

## Installation

### Server Installation (on Raspberry Pi)

Use the installation script to set up the server on your Raspberry Pi:

```bash
./scripts/install_remote_keyboard_server_fixed.sh --host <raspberry_pi_ip> --password <raspberry_pi_password>
```

This script will:
- Copy the necessary files to the Raspberry Pi
- Install required dependencies
- Set up a systemd service to run the server automatically

For detailed installation instructions, see [Remote Keyboard Server Installation Guide](../docs/remote_keyboard_server_installation.md).

### Client Configuration (on your computer)

1. Update your `.env` file with the Raspberry Pi connection details:

```
RPI_HOST=192.168.1.100  # Replace with your Raspberry Pi's IP address
RPI_USER=pi             # Replace with your Raspberry Pi username
RPI_PASSWORD=raspberry  # Replace with your Raspberry Pi password
```

2. Make sure you have the required Python packages installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To check the connection to the Raspberry Pi:

```bash
python examples/remote_keyboard_control_fixed.py --check-connection
```

To list available keyboard devices on the Raspberry Pi:

```bash
python examples/remote_keyboard_control_fixed.py --list
```

To type text on the remote keyboard:

```bash
python examples/remote_keyboard_control_fixed.py --device-id keyboard_01 --text "Hello, world!"
```

To press a specific key:

```bash
python examples/remote_keyboard_control_fixed.py --device-id keyboard_01 --key enter
```

To press a hotkey combination:

```bash
python examples/remote_keyboard_control_fixed.py --device-id keyboard_01 --hotkey ctrl,a
```

### Running the Demo

To run a demo sequence that demonstrates various keyboard actions:

```bash
python examples/remote_keyboard_control_fixed.py
```

This will:
1. List available keyboards on the Raspberry Pi
2. Type some text
3. Press Enter
4. Type more text
5. Press Ctrl+A to select all text

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Raspberry Pi:

1. Check that the Raspberry Pi is powered on and connected to the network
2. Verify that the IP address in your `.env` file is correct
3. Make sure the UnitAPI server is running on the Raspberry Pi
4. Check the server status:

```bash
python scripts/ssh_connect_wrapper.sh <username>@<raspberry_pi_ip> <password> -c 'systemctl status unitapi-keyboard.service'
```

### Local Keyboard Control Issue

If the script is controlling your local keyboard instead of the remote one:

1. Make sure you're using the fixed version of the client script (`remote_keyboard_control_fixed.py`)
2. Check that the connection to the remote server is successful
3. Verify that the keyboard device is registered on the remote server

## Advanced Configuration

### Custom Keyboard Device

You can specify a custom keyboard device ID and name when starting the server:

```bash
python examples/remote_keyboard_server.py --device-id custom_keyboard --name "My Custom Keyboard"
```

### Multiple Keyboards

You can run multiple instances of the server with different device IDs to control multiple keyboards:

```bash
python examples/remote_keyboard_server.py --device-id keyboard_01 --port 7890
python examples/remote_keyboard_server.py --device-id keyboard_02 --port 7891
```

## Security Considerations

- The remote keyboard control system does not include authentication by default
- Consider running the server on a private network
- Use SSH tunneling for secure remote access
- Be cautious when allowing remote keyboard control, as it can potentially execute commands on the Raspberry Pi

## Further Reading

- [Remote Keyboard Server Installation Guide](../docs/remote_keyboard_server_installation.md)
- [UnitAPI Documentation](../docs/index.md)
- [Input Devices Documentation](../docs/device_types.md)
