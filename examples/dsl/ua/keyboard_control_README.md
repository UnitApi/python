# UnitAPI DSL Keyboard Control Example

This example demonstrates how to use UnitAPI's Domain Specific Language (DSL) in `.ua` format to control a keyboard, allowing you to send text from one PC to another (or to the same PC).

## Files

- `keyboard_server.ua` - DSL configuration for the keyboard server
- `keyboard_client.ua` - DSL configuration for the keyboard client (sends predefined text)
- `keyboard_client_interactive.ua` - DSL configuration for an interactive keyboard client (allows typing custom text)
- `test_keyboard_control.py` - Python script to run the server and client configurations

## Setup

1. Make sure UnitAPI is installed on both PCs (or just one PC if you're testing locally)
2. Copy the `.ua` configuration files and the test script to both PCs

## Usage

### Running on a Single PC (PC1 to PC1)

1. Start the keyboard server:
   ```bash
   python test_keyboard_control.py --mode server
   ```

2. In another terminal, run the client to send predefined text:
   ```bash
   python test_keyboard_control.py --mode client
   ```

   Or run the interactive client to type custom text:
   ```bash
   python test_keyboard_control.py --mode interactive
   ```

### Running on Two PCs (PC1 to PC2)

1. On PC2 (the target PC), start the keyboard server:
   ```bash
   python test_keyboard_control.py --mode server
   ```

2. On PC1 (the source PC), run the client, specifying the IP address of PC2:
   ```bash
   python test_keyboard_control.py --mode client --host 192.168.1.102
   ```

   Or run the interactive client:
   ```bash
   python test_keyboard_control.py --mode interactive --host 192.168.1.102
   ```

## Command Line Options

The `test_keyboard_control.py` script supports the following options:

- `--mode {server,client,interactive}`: Run mode (required)
- `--server-config FILENAME`: Path to the server configuration file (default: keyboard_server.ua)
- `--client-config FILENAME`: Path to the client configuration file (default: keyboard_client.ua)
- `--interactive-config FILENAME`: Path to the interactive client configuration file (default: keyboard_client_interactive.ua)
- `--host HOST`: Server host (for client mode, default: localhost)
- `--port PORT`: Server port (for client mode, default: 7890)
- `--text TEXT`: Text to type (for client mode, default: "Hello from UnitAPI DSL!")

## Examples

1. Run the server on PC2 with IP 192.168.1.102:
   ```bash
   python test_keyboard_control.py --mode server
   ```

2. Send custom text from PC1 to PC2:
   ```bash
   python test_keyboard_control.py --mode client --host 192.168.1.102 --text "This is a test message from PC1"
   ```

3. Run the interactive client on PC1 to continuously send text to PC2:
   ```bash
   python test_keyboard_control.py --mode interactive --host 192.168.1.102
   ```

## How It Works

1. The keyboard server:
   - Registers a keyboard device with the UnitAPI server
   - Sets up command handlers for typing text, pressing keys, and hotkeys
   - Starts the server on the specified host and port

2. The keyboard client:
   - Connects to the keyboard server
   - Sends commands to type text, press keys, or hotkeys

3. The interactive keyboard client:
   - Connects to the keyboard server
   - Prompts the user for text input
   - Sends the entered text to the remote keyboard
   - Continues until the user types 'exit'

## Customizing the Configurations

You can modify the `.ua` configuration files to change the behavior:

- Change the server host and port in `keyboard_server.ua`
- Modify the predefined text in `keyboard_client.ua`
- Add additional commands or key sequences
- Create more complex pipelines for advanced keyboard control

## Troubleshooting

- Make sure both PCs are on the same network and can reach each other
- Check that the server is running before starting the client
- Verify that the host and port are correctly specified
- If using a firewall, ensure that the port (default: 7890) is open
