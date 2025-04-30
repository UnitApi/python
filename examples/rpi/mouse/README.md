# Raspberry Pi Mouse Examples for UnitAPI

This directory contains examples for controlling a mouse on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a mouse server on the Raspberry Pi and control it remotely from a client application.

## Files

- `mouse_server.py`: Server that runs on the Raspberry Pi and exposes mouse functionality through UnitAPI
- `mouse_client.py`: Client that connects to the server and controls the mouse remotely

## Prerequisites

- Raspberry Pi (any model)
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAutoGUI installed (`pip install pyautogui`)

## Server Setup

The mouse server runs on the Raspberry Pi and exposes mouse functionality through UnitAPI. It registers a mouse device with the UnitAPI server and handles commands for mouse movement, clicks, scrolling, and drag operations.

### Running the Server

```bash
# Run on the Raspberry Pi
python mouse_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--device-id`: Custom mouse device ID (default: mouse_rpi)
- `--name`: Custom mouse device name (default: Raspberry Pi Mouse)

## Client Usage

The mouse client connects to the server and controls the mouse remotely. It provides methods for moving the mouse, clicking, scrolling, and performing drag operations.

### Running the Client

```bash
# Connect to a local server
python mouse_client.py --demo movement

# Connect to a remote Raspberry Pi
python mouse_client.py --host 192.168.1.100 --port 7890 --demo all
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: movement, click, scroll, drag, all)
- `--x`: X coordinate for move_to command
- `--y`: Y coordinate for move_to command
- `--dx`: X delta for move_relative command
- `--dy`: Y delta for move_relative command
- `--button`: Mouse button for click commands (choices: left, right, middle)
- `--scroll-amount`: Scroll amount (positive for up, negative for down)

### Demo Modes

The client provides several demo modes:

1. **Movement Demo** (`--demo movement`): Demonstrates moving the mouse in patterns (square, circle)
2. **Click Demo** (`--demo click`): Demonstrates different types of mouse clicks (left, right, double)
3. **Scroll Demo** (`--demo scroll`): Demonstrates scrolling up and down
4. **Drag Demo** (`--demo drag`): Demonstrates dragging operations
5. **All Demos** (`--demo all`): Runs all demos in sequence

### Custom Commands

You can also use the client to execute specific mouse commands:

```bash
# Move to specific coordinates
python mouse_client.py --x 500 --y 500

# Move by a relative amount
python mouse_client.py --dx 100 --dy -50

# Click a specific button
python mouse_client.py --button right

# Scroll up or down
python mouse_client.py --scroll-amount 10
```

## Supported Mouse Operations

The mouse examples support the following operations:

- **Move To**: Move mouse cursor to absolute position
- **Move Relative**: Move mouse cursor by a relative amount
- **Click**: Perform a mouse click (left, right, or middle button)
- **Double Click**: Perform a mouse double-click
- **Button Down**: Press and hold a mouse button
- **Button Up**: Release a mouse button
- **Scroll**: Scroll the mouse wheel
- **Drag**: Perform a drag operation from current position to target position

## Integration with Other Applications

The mouse functionality can be integrated with other applications running on the Raspberry Pi. For example:

- Control graphical user interfaces
- Automate testing of GUI applications
- Create custom input devices for specific applications
- Implement remote control for Raspberry Pi-based kiosks or displays

## Security Considerations

Remote mouse control provides powerful capabilities but also introduces security risks. Consider the following:

- Run the server on a secure, private network
- Use UnitAPI's authentication and encryption features
- Be cautious about allowing remote mouse control in sensitive environments
- Consider implementing additional access controls based on your specific requirements

## Troubleshooting

1. **Connection Issues**: Ensure the server is running and accessible from the client's network
2. **Permission Issues**: Some systems may require additional permissions for mouse control
3. **Coordinate Issues**: Screen coordinates are relative to the Raspberry Pi's display resolution
4. **Performance Issues**: Reduce the frequency of mouse operations if experiencing lag

## Example Use Cases

1. **Remote Control**: Control applications on a headless Raspberry Pi
2. **Automation**: Automate repetitive mouse tasks
3. **Kiosk Systems**: Implement controlled mouse input for kiosk applications
4. **Accessibility**: Create custom mouse interfaces for accessibility purposes
