# Raspberry Pi Keyboard Examples for UnitAPI

This directory contains examples for controlling a keyboard on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a keyboard server on the Raspberry Pi and control it remotely from a client application.

## Files

- `keyboard_server.py`: Server that runs on the Raspberry Pi and exposes keyboard functionality through UnitAPI
- `keyboard_client.py`: Client that connects to the server and controls the keyboard remotely

## Prerequisites

- Raspberry Pi (any model)
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAutoGUI installed (`pip install pyautogui`)

## Server Setup

The keyboard server runs on the Raspberry Pi and exposes keyboard functionality through UnitAPI. It registers a keyboard device with the UnitAPI server and handles commands for key presses, text typing, and keyboard shortcuts.

### Running the Server

```bash
# Run on the Raspberry Pi
python keyboard_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--device-id`: Custom keyboard device ID (default: keyboard_rpi)
- `--name`: Custom keyboard device name (default: Raspberry Pi Keyboard)

## Client Usage

The keyboard client connects to the server and controls the keyboard remotely. It provides methods for typing text, pressing keys, and using keyboard shortcuts.

### Running the Client

```bash
# Connect to a local server
python keyboard_client.py --demo typing

# Connect to a remote Raspberry Pi
python keyboard_client.py --host 192.168.1.100 --port 7890 --demo all
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: typing, hotkey, sequence, all)
- `--text`: Text to type (for custom commands)
- `--key`: Key to press (for custom commands)
- `--hotkey`: Hotkey to press (comma-separated keys, e.g., ctrl,s)

### Demo Modes

The client provides several demo modes:

1. **Typing Demo** (`--demo typing`): Demonstrates typing text and pressing Enter
2. **Hotkey Demo** (`--demo hotkey`): Demonstrates using keyboard shortcuts like Ctrl+A
3. **Key Sequence Demo** (`--demo sequence`): Demonstrates using arrow keys and modifier keys
4. **All Demos** (`--demo all`): Runs all demos in sequence

### Custom Commands

You can also use the client to execute specific keyboard commands:

```bash
# Type specific text
python keyboard_client.py --text "Hello, world!"

# Press a specific key
python keyboard_client.py --key enter

# Press a specific hotkey combination
python keyboard_client.py --hotkey ctrl,s
```

## Supported Keyboard Operations

The keyboard examples support the following operations:

- **Key Down**: Press and hold a key
- **Key Up**: Release a key
- **Press Key**: Press and release a key
- **Type Text**: Type a sequence of characters
- **Press Hotkey**: Press a combination of keys simultaneously
- **Release All Keys**: Release all currently pressed keys

## Integration with Other Applications

The keyboard functionality can be integrated with other applications running on the Raspberry Pi. For example:

- Control text editors or command-line interfaces
- Automate form filling in web browsers
- Control games or other applications
- Implement custom keyboard shortcuts for specific tasks

## Security Considerations

Remote keyboard control provides powerful capabilities but also introduces security risks. Consider the following:

- Run the server on a secure, private network
- Use UnitAPI's authentication and encryption features
- Be cautious about allowing remote keyboard control in sensitive environments
- Consider implementing additional access controls based on your specific requirements

## Troubleshooting

1. **Connection Issues**: Ensure the server is running and accessible from the client's network
2. **Permission Issues**: Some systems may require additional permissions for keyboard control
3. **Key Mapping Issues**: Different keyboard layouts may require adjustments to key mappings
4. **Stuck Keys**: If keys appear to be stuck, use the `release_all_keys` command to reset the keyboard state

## Example Use Cases

1. **Remote Control**: Control applications on a headless Raspberry Pi
2. **Automation**: Automate repetitive keyboard tasks
3. **Kiosk Systems**: Implement controlled keyboard input for kiosk applications
4. **Accessibility**: Create custom keyboard interfaces for accessibility purposes
