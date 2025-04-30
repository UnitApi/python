# Miscellaneous PC Examples for UnitAPI

This directory contains miscellaneous examples for UnitAPI that don't fit into the specific device categories. These examples demonstrate various features and capabilities of UnitAPI.

## Files

- `device_discovery.py`: Example demonstrating how to discover UnitAPI devices on the network
- `ssh_connector.py`: Example demonstrating how to connect to remote devices using SSH
- `input_devices.py`: Example demonstrating how to work with multiple input devices

## Device Discovery

The device discovery example shows how to find UnitAPI devices on the network. This is useful for discovering available devices without knowing their specific addresses.

### Running the Device Discovery Example

```bash
# Run the device discovery example
python examples/pc/misc/device_discovery.py
```

This example demonstrates:
- Setting up a discovery service
- Broadcasting device availability
- Discovering devices on the network
- Handling device discovery events

## SSH Connector

The SSH connector example shows how to connect to remote devices using SSH. This is useful for securely connecting to and controlling devices on remote machines.

### Running the SSH Connector Example

```bash
# Run the SSH connector example
python examples/pc/misc/ssh_connector.py --host remote-host --user username
```

Options:
- `--host`: Remote host to connect to
- `--user`: Username for SSH authentication
- `--password`: Password for SSH authentication (or use key-based authentication)
- `--port`: SSH port (default: 22)

This example demonstrates:
- Establishing SSH connections
- Executing commands on remote machines
- Transferring files securely
- Managing remote sessions

## Input Devices

The input devices example shows how to work with multiple input devices simultaneously. This is useful for applications that need to handle input from various sources.

### Running the Input Devices Example

```bash
# Run the input devices example
python examples/pc/misc/input_devices.py
```

This example demonstrates:
- Creating multiple input devices
- Handling input from different sources
- Coordinating input events
- Managing device lifecycles

## Integration with Other Examples

These miscellaneous examples can be combined with the device-specific examples to create more complex applications. For example:

1. Use device discovery to find available devices
2. Connect to remote devices using SSH
3. Control specific devices using the device-specific examples

## Additional Resources

For more information about UnitAPI and its capabilities, see the documentation in the `docs/` directory.
