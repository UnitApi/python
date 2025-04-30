# PC Keyboard Examples for UnitAPI

This directory contains examples for controlling a keyboard on a PC using UnitAPI. These examples demonstrate how to use the keyboard device locally and how to set up a keyboard server for remote control.

## Files

- `keyboard_client.py`: Client that demonstrates local keyboard control
- `keyboard_server.py`: Server that exposes keyboard functionality through UnitAPI
- `remote_keyboard_client.py`: Client that connects to the server and controls the keyboard remotely

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAutoGUI installed (`pip install pyautogui`)
- python-dotenv (for remote control example)

## Local Keyboard Control

The keyboard client demonstrates how to use the keyboard device locally to type text, press keys, and use keyboard shortcuts.

### Running the Local Client

```bash
# Run the local keyboard example
python examples/pc/keyboard/keyboard_client.py
```

This example demonstrates:
- Creating a keyboard device
- Typing text
- Pressing individual keys
- Using keyboard shortcuts
- Handling special keys

## Remote Keyboard Control

The keyboard server and remote client demonstrate how to control a keyboard remotely using UnitAPI.

### Running the Server

```bash
# Run on the PC you want to control
python examples/pc/keyboard/keyboard_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--device-id`: Custom keyboard device ID (default: keyboard_01)
- `--name`: Custom keyboard device name (default: Raspberry Pi Keyboard)

### Running the Remote Client

```bash
# Connect to a local server
python examples/pc/keyboard/remote_keyboard_client.py --demo typing

# Connect to a remote PC
python examples/pc/keyboard/remote_keyboard_client.py --host 192.168.1.100 --port 7890 --demo all
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--list`: List available remote keyboards
- `--device-id`: Specific remote keyboard device ID to use
- `--text`: Text to type on the remote keyboard
- `--key`: Key to press on the remote keyboard
- `--hotkey`: Hotkey to press (comma-separated keys, e.g., ctrl,s)

### Demo Modes

The remote client provides several demo modes:

1. **Typing Demo**: Demonstrates typing text and pressing Enter
2. **Hotkey Demo**: Demonstrates using keyboard shortcuts like Ctrl+A
3. **Key Sequence Demo**: Demonstrates using arrow keys and modifier keys
4. **All Demos**: Runs all demos in sequence

## Supported Keyboard Operations

The keyboard examples support the following operations:

- **Key Down**: Press and hold a key
- **Key Up**: Release a key
- **Press Key**: Press and release a key
- **Type Text**: Type a sequence of characters
- **Press Hotkey**: Press a combination of keys simultaneously
- **Release All Keys**: Release all currently pressed keys

## Integration with Other Applications

The keyboard functionality can be integrated with other applications:

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

1. **Remote Control**: Control applications on a headless PC
2. **Automation**: Automate repetitive keyboard tasks
3. **Kiosk Systems**: Implement controlled keyboard input for kiosk applications
4. **Accessibility**: Create custom keyboard interfaces for accessibility purposes
