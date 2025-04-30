#!/usr/bin/env python3
"""
SSH Connector Example

This script demonstrates how to use the SSHConnector class to establish an SSH connection
to a remote device and execute commands.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add scripts directory to path to import SSHConnector
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
try:
    from ssh_connect import SSHConnector
except ImportError:
    print("Error: Could not import SSHConnector from ssh_connect.py")
    print("Make sure ssh_connect.py is in the scripts directory")
    sys.exit(1)


async def run_remote_commands(host, user, password=None, identity_file=None, port=22):
    """
    Run a series of commands on a remote device.
    
    Args:
        host: Remote host address
        user: SSH username
        password: SSH password (optional)
        identity_file: Path to SSH identity file (optional)
        port: SSH port (default: 22)
    """
    print(f"Connecting to {host} as {user}...")
    
    # Create SSH connector
    ssh = SSHConnector(
        username=user,
        server=host,
        password=password,
        port=port,
        identity_file=identity_file,
        verbose=True
    )
    
    # Connect to server
    if not ssh.connect():
        print("Failed to connect to remote device")
        return
    
    try:
        # Execute commands
        print("\n=== System Information ===")
        exit_code, stdout, stderr = ssh.execute_command("uname -a")
        if stdout:
            print(stdout)
        
        print("\n=== Disk Usage ===")
        exit_code, stdout, stderr = ssh.execute_command("df -h")
        if stdout:
            print(stdout)
        
        print("\n=== Memory Usage ===")
        exit_code, stdout, stderr = ssh.execute_command("free -h")
        if stdout:
            print(stdout)
        
        print("\n=== Network Interfaces ===")
        exit_code, stdout, stderr = ssh.execute_command("ip addr")
        if stdout:
            print(stdout)
        
        print("\n=== Running Processes ===")
        exit_code, stdout, stderr = ssh.execute_command("ps aux | head -10")
        if stdout:
            print(stdout)
        
    finally:
        # Disconnect
        ssh.disconnect()
        print("Disconnected from remote device")


async def main():
    """
    Main function to parse arguments and run remote commands.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get connection details from .env
    host = os.getenv('SSH_SERVER', os.getenv('RPI_HOST', ''))
    user = os.getenv('SSH_USER', os.getenv('RPI_USER', 'pi'))
    password = os.getenv('SSH_PASSWORD', os.getenv('RPI_PASSWORD', ''))
    identity_file = os.getenv('SSH_IDENTITY_FILE', '')
    port = int(os.getenv('SSH_PORT', '22'))
    
    # Check if host is provided
    if not host:
        print("Please set SSH_SERVER or RPI_HOST in .env file")
        return 1
    
    # Check if password or identity file is provided
    if not password and not identity_file:
        print("Please set SSH_PASSWORD/RPI_PASSWORD or SSH_IDENTITY_FILE in .env file")
        return 1
    
    # Display connection details
    print("=== SSH Connection Details ===")
    print(f"Host: {host}")
    print(f"User: {user}")
    if password:
        print(f"Password: {'*' * len(password)}")
    if identity_file:
        print(f"Identity File: {identity_file}")
    print(f"Port: {port}")
    print("=============================")
    
    # Run remote commands
    await run_remote_commands(
        host=host,
        user=user,
        password=password,
        identity_file=identity_file,
        port=port
    )
    
    return 0


if __name__ == "__main__":
    asyncio.run(main())
