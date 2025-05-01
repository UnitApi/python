# Remote Keyboard Control Example

This example demonstrates how to control a keyboard on a remote Raspberry Pi device using UnitAPI. The script uses connection details (host, username, password) from a `.env` file.

## Prerequisites

1. A Raspberry Pi with UnitAPI server installed and running
2. Python 3.6+ on both the client and Raspberry Pi
3. Required Python packages:
   - `unitapi`
   - `python-dotenv`

## Setup

1. Make sure the UnitAPI server is running on your Raspberry Pi
2. Update the `.env` file with your Raspberry Pi connection details:
   ```
   RPI_HOST=192.168.1.100  # Replace with your Raspberry Pi's IP address
   RPI_USER=pi             # Replace with your Raspberry Pi username
   RPI_PASSWORD=raspberry  # Replace with your Raspberry Pi password
   ```

3. Make sure the keyboard device is registered on the Raspberry Pi UnitAPI server

## Usage

### List available keyboards on the remote device

```bash
python examples/remote_keyboard_control.py --list
```

### Type text on a specific keyboard

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --text "Hello, world!"
```

### Press a key on a specific keyboard

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --key "enter"
```

### Press a hotkey combination on a specific keyboard

```bash
python examples/remote_keyboard_control.py --device-id keyboard_01 --hotkey "ctrl,a"
```

### Run a demo sequence

If no specific action is provided, the script will run a demo sequence on the first available keyboard:

```bash
python examples/remote_keyboard_control.py
```

## Troubleshooting

If no keyboards are found, make sure:

1. The UnitAPI server is running on your Raspberry Pi
2. The keyboard device is registered with the server
3. The connection details in the `.env` file are correct
4. There are no network issues preventing connection to the Raspberry Pi

You can start the device discovery service on the Raspberry Pi with:

```bash
python examples/device_discovery.py
```

## How It Works

1. The script loads connection details from the `.env` file
2. It connects to the UnitAPI server on the Raspberry Pi
3. It lists available keyboard devices or performs the specified action
4. Commands are sent to the remote keyboard device through the UnitAPI client

The script demonstrates:
- Connecting to a remote UnitAPI server
- Listing available devices
- Typing text on a remote keyboard
- Pressing keys and hotkey combinations
- Using environment variables for configuration
