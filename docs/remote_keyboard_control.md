# Remote Keyboard Control

This document describes how to set up and use the UnitAPI Remote Keyboard Control feature, which allows you to control a keyboard on a remote Raspberry Pi device.

## Overview

The Remote Keyboard Control feature consists of two main components:

1. **Server Component** (`remote_keyboard_server.py`): Runs on the Raspberry Pi and registers a keyboard device with the UnitAPI server.
2. **Client Component** (`remote_keyboard_control.py`): Runs on your local machine and sends commands to the remote keyboard.

This setup allows you to remotely type text, press keys, and execute keyboard shortcuts on the Raspberry Pi from your local machine.

## Setup Instructions

### 1. Server Setup (on Raspberry Pi)

You can set up the server component manually or use the provided installation script.

#### Option A: Using the Installation Script

The easiest way to set up the server is to use the provided installation script:

```bash
./scripts/install_remote_keyboard_server.sh --host <RPI_IP_ADDRESS> --user pi --password <RPI_PASSWORD>
```

This script will:
- Copy the necessary files to the Raspberry Pi
- Install required dependencies
- Set up a systemd service to run the server automatically at boot
- Start the server

#### Option B: Manual Setup

If you prefer to set up the server manually:

1. Copy the server script to the Raspberry Pi:
   ```bash
   scp examples/remote_keyboard_server.py pi@<RPI_IP_ADDRESS>:/home/pi/
   ```

2. Install required dependencies on the Raspberry Pi:
   ```bash
   ssh pi@<RPI_IP_ADDRESS>
   sudo apt-get update
   sudo apt-get install -y python3-pip
   pip3 install unitapi python-dotenv pyautogui
   ```

3. Run the server script:
   ```bash
   python3 remote_keyboard_server.py
   ```

### 2. Client Setup (on your local machine)

1. Update the `.env` file with your Raspberry Pi connection details:
   ```
   RPI_HOST=192.168.1.100  # Replace with your Raspberry Pi's IP address
   RPI_USER=pi             # Replace with your Raspberry Pi username
   RPI_PASSWORD=raspberry  # Replace with your Raspberry Pi password
   ```

2. Run the client script to test the connection:
   ```bash
   python examples/remote_keyboard_control.py --list
   ```

## Usage

### List Available Keyboards

```bash
python examples/remote_keyboard_control.py --list
```

### Type Text

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --text "Hello, world!"
```

### Press a Key

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --key "enter"
```

### Press a Hotkey Combination

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --hotkey "ctrl,a"
```

### Run a Demo Sequence

```bash
python examples/remote_keyboard_control.py
```

## How It Works

1. The server script (`remote_keyboard_server.py`) runs on the Raspberry Pi and:
   - Creates a UnitAPI server
   - Registers a keyboard device
   - Defines command handlers for typing text, pressing keys, and pressing hotkeys

2. The client script (`remote_keyboard_control.py`) runs on your local machine and:
   - Connects to the UnitAPI server on the Raspberry Pi
   - Sends commands to control the keyboard

3. When you run a command like `--text "Hello, world!"`, the client:
   - Sends a command to the server with the text to type
   - The server receives the command and uses the keyboard device to type the text

## Troubleshooting

### No Keyboards Found

If the client reports "No keyboards found on remote device":

1. Make sure the server is running on the Raspberry Pi:
   ```bash
   ssh pi@<RPI_IP_ADDRESS> "systemctl status unitapi-keyboard.service"
   ```

2. If the service is not running, start it:
   ```bash
   ssh pi@<RPI_IP_ADDRESS> "sudo systemctl start unitapi-keyboard.service"
   ```

3. Check if the server is listening on the correct port:
   ```bash
   ssh pi@<RPI_IP_ADDRESS> "netstat -tuln | grep 7890"
   ```

4. Make sure there are no firewall rules blocking the connection:
   ```bash
   ssh pi@<RPI_IP_ADDRESS> "sudo iptables -L"
   ```

### Connection Issues

If you're having trouble connecting to the Raspberry Pi:

1. Make sure the Raspberry Pi is on the same network as your local machine
2. Verify the IP address is correct
3. Check that SSH is enabled on the Raspberry Pi
4. Try pinging the Raspberry Pi to check connectivity:
   ```bash
   ping <RPI_IP_ADDRESS>
   ```

## Advanced Configuration

### Changing the Server Port

By default, the server runs on port 7890. To use a different port:

1. On the server side:
   ```bash
   python3 remote_keyboard_server.py --port 8000
   ```

2. On the client side:
   ```bash
   python examples/remote_keyboard_control.py --port 8000 --list
   ```

### Using Multiple Keyboard Devices

You can register multiple keyboard devices with different IDs:

```bash
python3 remote_keyboard_server.py --device-id keyboard_02 --name "Second Keyboard"
```

Then control them individually from the client:

```bash
python examples/remote_keyboard_control.py --device-id keyboard_02 --text "Hello from second keyboard"
```

## Security Considerations

- The current implementation uses plain text passwords in the `.env` file, which is not secure for production use
- Consider using SSH keys for authentication instead of passwords
- The UnitAPI server does not implement authentication by default, so anyone with network access can control the keyboard
- For production use, consider implementing proper authentication and encryption

## Further Development

Possible enhancements for the Remote Keyboard Control feature:

- Add authentication to the UnitAPI server
- Implement encryption for the communication
- Create a graphical user interface for the client
- Add support for more complex keyboard operations
- Implement keyboard macros and sequences
