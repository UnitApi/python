# SSH Tools for UnitAPI

This document describes the SSH tools available in the UnitAPI project for connecting to and managing remote devices.

## Overview

The UnitAPI project includes Python-based SSH tools that allow for easy connection to remote devices, such as Raspberry Pi, for installation and management of UnitAPI services. These tools provide a more robust and flexible alternative to the bash-based scripts.

## Available Tools

### 1. SSH Connector (`scripts/ssh_connect.py`)

A Python implementation of an SSH client with URL-like parameter parsing, similar to the `ssh_connect.sh` bash script. This tool provides a simple interface for establishing SSH connections to remote devices.

#### Features

- URL-like connection format (`user@server`)
- Password-based authentication
- Key-based authentication
- Command execution
- Interactive shell
- Verbose logging

#### Usage

```bash
python scripts/ssh_connect.py [user@server] [password] [options]
```

#### Options

- `-h, --help`: Show help message
- `-i, --identity FILE`: Specify an identity file for key-based authentication
- `-P, --port PORT`: Specify SSH port (default: 22)
- `-v, --verbose`: Enable verbose SSH output
- `-c, --command CMD`: Execute a command on the remote server

#### Examples

```bash
# Connect with password
python scripts/ssh_connect.py pi@192.168.1.100 raspberry

# Connect with identity file
python scripts/ssh_connect.py pi@192.168.1.100 -i ~/.ssh/id_rsa

# Connect with custom port
python scripts/ssh_connect.py admin@server.local mypassword -P 2222

# Execute a command
python scripts/ssh_connect.py pi@192.168.1.100 -c 'ls -la'
```

### 2. Remote Keyboard Server Installer (`scripts/install_remote_keyboard_server.py`)

A Python implementation of the Remote Keyboard Server installation script. This tool automates the process of installing and configuring the UnitAPI Remote Keyboard Server on a Raspberry Pi.

#### Features

- SSH connection to Raspberry Pi
- Installation of required packages
- Setup of Python environment
- Configuration of systemd service
- Service management

#### Usage

```bash
python scripts/install_remote_keyboard_server.py [options]
```

#### Options

- `--host HOST`: Raspberry Pi host address
- `--user USER`: SSH username (default: pi)
- `--password PASSWORD`: SSH password
- `--port PORT`: SSH port (default: 22)
- `--install-dir DIR`: Installation directory on Raspberry Pi (default: /home/pi/unitapi)
- `--server-port PORT`: UnitAPI server port (default: 7890)
- `--identity FILE`: Path to SSH identity file for key-based authentication
- `--verbose`: Enable verbose output

#### Examples

```bash
# Install with password authentication
python scripts/install_remote_keyboard_server.py --host 192.168.1.100 --password raspberry

# Install with key-based authentication
python scripts/install_remote_keyboard_server.py --host 192.168.1.100 --identity ~/.ssh/id_rsa

# Install with custom server port
python scripts/install_remote_keyboard_server.py --host 192.168.1.100 --password raspberry --server-port 8000
```

### 3. SSH Connector Example (`examples/ssh_connector_example.py`)

A simple example script that demonstrates how to use the SSHConnector class to establish an SSH connection to a remote device and execute commands.

#### Features

- Connects to a remote device using the SSHConnector class
- Executes a series of system information commands
- Displays the results
- Supports both password and key-based authentication
- Loads connection details from .env file

#### Usage

```bash
python examples/ssh_connector_example.py
```

#### Example Output

```
=== SSH Connection Details ===
Host: 192.168.1.100
User: pi
Password: ********
Port: 22
=============================
Connecting to 192.168.1.100 as pi...
Attempting to connect to 192.168.1.100 as pi...
Using password authentication
Successfully connected to 192.168.1.100

=== System Information ===
Linux raspberrypi 5.15.0-1033-raspi #36-Ubuntu SMP PREEMPT Fri Mar 17 15:20:57 UTC 2023 aarch64 aarch64 aarch64 GNU/Linux

=== Disk Usage ===
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G  5.8G   22G  21% /
...

=== Memory Usage ===
              total        used        free      shared  buff/cache   available
Mem:          3.8Gi       427Mi       2.9Gi        33Mi       511Mi       3.3Gi
Swap:         1.0Gi          0B       1.0Gi

...

Disconnected from remote device
```

## Environment Variables

All tools support loading configuration from a `.env` file. The following environment variables are recognized:

### SSH Connector

- `SSH_USER`: Default SSH username
- `SSH_SERVER`: Default SSH server address
- `SSH_PASSWORD`: Default SSH password
- `SSH_PORT`: Default SSH port
- `SSH_IDENTITY_FILE`: Default SSH identity file
- `SSH_VERBOSE`: Enable verbose output (true/false)

### Remote Keyboard Server Installer

- `RPI_HOST`: Raspberry Pi host address
- `RPI_USER`: SSH username
- `RPI_PASSWORD`: SSH password
- `INSTALL_DIR`: Installation directory on Raspberry Pi
- `SERVER_PORT`: UnitAPI server port

## Dependencies

These tools require the following Python packages:

- `paramiko`: SSH implementation for Python
- `python-dotenv`: Loading environment variables from .env files

These dependencies are included in the project's `requirements.txt` file.

## Comparison with Bash Scripts

The Python-based SSH tools offer several advantages over the bash-based scripts:

1. **Cross-platform compatibility**: Works on Windows, macOS, and Linux
2. **Better error handling**: More robust error detection and reporting
3. **Object-oriented design**: Modular and reusable components
4. **Enhanced security**: Better handling of credentials and connections
5. **Improved maintainability**: Easier to extend and modify

## Future Improvements

Potential future improvements for the SSH tools include:

1. Support for SSH tunneling
2. Integration with other UnitAPI components
3. GUI interface for connection management
4. Support for additional authentication methods
5. Batch command execution
