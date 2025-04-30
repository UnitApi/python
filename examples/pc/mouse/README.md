# PC Mouse Examples for UnitAPI

This directory contains examples for controlling a mouse on a PC using UnitAPI. These examples demonstrate how to use the mouse device locally and how to set up a mouse server for remote control.

## Files

- `mouse_client.py`: Client that demonstrates local mouse control
- `mouse_pyautogui_client.py`: Client that demonstrates mouse control using PyAutoGUI
- `mouse_server.py`: Server that exposes mouse functionality through UnitAPI for remote control

## Prerequisites

- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- PyAutoGUI installed (`pip install pyautogui`)

## Local Mouse Control

The mouse client demonstrates how to use the mouse device locally to move the cursor, click, and perform other mouse operations.

### Running the Local Client

```bash
# Run the standard mouse example
python examples/pc/mouse/mouse_client.py

# Run the PyAutoGUI mouse example
python examples/pc/mouse/mouse_pyautogui_client.py
```

These examples demonstrate:
- Creating a mouse device
- Moving the mouse cursor to absolute positions
- Moving the mouse cursor relatively
- Clicking and double-clicking
- Pressing and releasing mouse buttons
- Scrolling
- Dragging objects

## Remote Mouse Control

The mouse server allows remote clients to control the mouse on a PC using UnitAPI.

### Running the Server

```bash
# Run on the PC you want to control
python examples/pc/mouse/mouse_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--device-id`: Custom mouse device ID (default: mouse_01)
- `--name`: Custom mouse device name (default: PC Mouse)

### Connecting to the Server

You can connect to the mouse server using the UnitAPI client:

```python
from unitapi.core.client import UnitAPIClient

async def control_remote_mouse():
    # Connect to the server
    client = UnitAPIClient(server_host="192.168.1.100", server_port=7890)
    
    # List available devices
    devices = await client.list_devices()
    
    # Find the mouse device
    mouse_devices = [d for d in devices if d.get('type') == 'mouse']
    if not mouse_devices:
        print("No mouse devices found")
        return
    
    mouse_device = mouse_devices[0]
    device_id = mouse_device.get('device_id')
    
    # Move the mouse
    await client.execute_command(
        device_id=device_id,
        command="move_to",
        params={"x": 500, "y": 500}
    )
    
    # Click the mouse
    await client.execute_command(
        device_id=device_id,
        command="click",
        params={"button": "left"}
    )
```

## Supported Mouse Operations

The mouse examples support the following operations:

- **Move To**: Move the mouse cursor to an absolute position
- **Move Relative**: Move the mouse cursor by a relative amount
- **Click**: Click a mouse button
- **Double Click**: Double-click a mouse button
- **Button Down**: Press and hold a mouse button
- **Button Up**: Release a mouse button
- **Scroll**: Scroll the mouse wheel
- **Drag**: Drag the mouse from the current position to a new position

## Integration with Other Applications

The mouse functionality can be integrated with other applications:

- Control GUI applications remotely
- Automate repetitive mouse tasks
- Create custom mouse interfaces for accessibility purposes
- Implement remote desktop functionality
- Create automated testing tools

## Security Considerations

Remote mouse control provides powerful capabilities but also introduces security risks. Consider the following:

- Run the server on a secure, private network
- Use UnitAPI's authentication and encryption features
- Be cautious about allowing remote mouse control in sensitive environments
- Consider implementing additional access controls based on your specific requirements

## Troubleshooting

1. **Connection Issues**: Ensure the server is running and accessible from the client's network
2. **Permission Issues**: Some systems may require additional permissions for mouse control
3. **Coordinate Issues**: Screen resolutions may differ between systems, affecting absolute positioning
4. **Performance Issues**: High latency networks may affect the responsiveness of mouse control

## Example Use Cases

1. **Remote Control**: Control applications on a headless PC
2. **Automation**: Automate repetitive mouse tasks
3. **Kiosk Systems**: Implement controlled mouse input for kiosk applications
4. **Accessibility**: Create custom mouse interfaces for accessibility purposes
5. **Testing**: Automate GUI testing with programmatic mouse control
