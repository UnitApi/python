#!/usr/bin/env python3
"""
Install and configure the UnitAPI Remote Keyboard Server on a Raspberry Pi

This script is a Python implementation of the install_remote_keyboard_server.sh bash script.
It uses the SSHConnector class to establish an SSH connection to a Raspberry Pi and
install the UnitAPI Remote Keyboard Server.
"""

import os
import sys
import argparse
import tempfile
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import the SSHConnector class from ssh_connect.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ssh_connect import SSHConnector
except ImportError:
    print("Error: Could not import SSHConnector from ssh_connect.py")
    print("Make sure ssh_connect.py is in the same directory as this script")
    sys.exit(1)


class RemoteKeyboardServerInstaller:
    def __init__(
            self,
            host: str,
            user: str = "pi",
            password: str = None,
            port: int = 22,
            install_dir: str = "/home/pi/unitapi",
            server_port: int = 7890,
            identity_file: str = None,
            verbose: bool = False
    ):
        """
        Initialize the Remote Keyboard Server Installer.

        Args:
            host: Raspberry Pi host address
            user: SSH username (default: pi)
            password: SSH password
            port: SSH port (default: 22)
            install_dir: Installation directory on the Raspberry Pi (default: /home/pi/unitapi)
            server_port: UnitAPI server port (default: 7890)
            identity_file: Path to SSH identity file for key-based authentication
            verbose: Enable verbose output
        """
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.install_dir = install_dir
        self.server_port = server_port
        self.identity_file = identity_file
        self.verbose = verbose
        
        # SSH connector
        self.ssh = None
    
    def log(self, message: str):
        """
        Log a message.
        
        Args:
            message: Message to log
        """
        print(message)
    
    def connect(self) -> bool:
        """
        Connect to the Raspberry Pi via SSH.
        
        Returns:
            True if connection was successful, False otherwise
        """
        self.log(f"Connecting to {self.host} as {self.user}...")
        
        # Create SSH connector
        self.ssh = SSHConnector(
            username=self.user,
            server=self.host,
            password=self.password,
            port=self.port,
            identity_file=self.identity_file,
            verbose=self.verbose
        )
        
        # Connect to server
        return self.ssh.connect()
    
    def execute_command(self, command: str) -> bool:
        """
        Execute a command on the Raspberry Pi.
        
        Args:
            command: Command to execute
            
        Returns:
            True if command was successful, False otherwise
        """
        if not self.ssh:
            self.log("Not connected to Raspberry Pi")
            return False
        
        exit_code, stdout, stderr = self.ssh.execute_command(command)
        
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        
        return exit_code == 0
    
    def create_installation_directory(self) -> bool:
        """
        Create the installation directory structure on the Raspberry Pi.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Creating installation directory structure...")
        return self.execute_command(f"mkdir -p {self.install_dir}/examples")
    
    def copy_files(self) -> bool:
        """
        Copy necessary files to the Raspberry Pi.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Copying files to Raspberry Pi...")
        
        # Get the project root directory (assuming this script is in the scripts/ directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Files to copy
        files = [
            "examples/remote_keyboard_server.py",
            "examples/device_discovery.py"
        ]
        
        success = True
        for file in files:
            local_path = os.path.join(project_root, file)
            remote_path = f"{self.install_dir}/{file}"
            
            # Create remote directory if needed
            remote_dir = os.path.dirname(remote_path)
            self.execute_command(f"mkdir -p {remote_dir}")
            
            # Use SCP to copy the file
            scp_command = f"scp -P {self.port} {local_path} {self.user}@{self.host}:{remote_path}"
            
            if self.identity_file:
                scp_command += f" -i {self.identity_file}"
            
            # Execute SCP command locally
            self.log(f"Copying {file}...")
            if os.system(scp_command) != 0:
                self.log(f"Error copying {file}")
                success = False
        
        return success
    
    def install_packages(self) -> bool:
        """
        Install required packages on the Raspberry Pi.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Installing required packages on Raspberry Pi...")
        return self.execute_command("sudo apt-get update && sudo apt-get install -y python3-pip python3-venv")
    
    def setup_python_environment(self) -> bool:
        """
        Set up Python environment and install dependencies.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Setting up Python environment and installing dependencies...")
        return self.execute_command(
            f"cd {self.install_dir} && "
            f"python3 -m venv venv && "
            f"source venv/bin/activate && "
            f"pip install unitapi python-dotenv pyautogui"
        )
    
    def create_systemd_service(self) -> bool:
        """
        Create systemd service for UnitAPI Remote Keyboard Server.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Creating systemd service for UnitAPI Remote Keyboard Server...")
        
        # Create service file content
        service_content = f"""[Unit]
Description=UnitAPI Remote Keyboard Server
After=network.target

[Service]
User={self.user}
WorkingDirectory={self.install_dir}
ExecStart={self.install_dir}/venv/bin/python {self.install_dir}/examples/remote_keyboard_server.py --port {self.server_port}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(service_content)
            temp_file_path = temp_file.name
        
        try:
            # Copy service file to Raspberry Pi
            scp_command = f"scp -P {self.port} {temp_file_path} {self.user}@{self.host}:/tmp/unitapi-keyboard.service"
            
            if self.identity_file:
                scp_command += f" -i {self.identity_file}"
            
            # Execute SCP command locally
            self.log("Copying service file...")
            if os.system(scp_command) != 0:
                self.log("Error copying service file")
                return False
            
            # Move service file to systemd directory and enable it
            self.log("Installing and enabling service...")
            return self.execute_command(
                "sudo mv /tmp/unitapi-keyboard.service /etc/systemd/system/ && "
                "sudo systemctl daemon-reload && "
                "sudo systemctl enable unitapi-keyboard.service"
            )
        finally:
            # Remove temporary file
            os.unlink(temp_file_path)
    
    def start_service(self) -> bool:
        """
        Start the UnitAPI Remote Keyboard Server service.
        
        Returns:
            True if successful, False otherwise
        """
        self.log("Starting UnitAPI Remote Keyboard Server service...")
        return self.execute_command("sudo systemctl start unitapi-keyboard.service")
    
    def check_service_status(self) -> bool:
        """
        Check the status of the UnitAPI Remote Keyboard Server service.
        
        Returns:
            True if service is running, False otherwise
        """
        self.log("Checking service status...")
        return self.execute_command("sudo systemctl status unitapi-keyboard.service")
    
    def install(self) -> bool:
        """
        Install and configure the UnitAPI Remote Keyboard Server.
        
        Returns:
            True if installation was successful, False otherwise
        """
        # Connect to Raspberry Pi
        if not self.connect():
            return False
        
        # Create installation directory
        if not self.create_installation_directory():
            return False
        
        # Copy files
        if not self.copy_files():
            return False
        
        # Install required packages
        if not self.install_packages():
            return False
        
        # Set up Python environment
        if not self.setup_python_environment():
            return False
        
        # Create systemd service
        if not self.create_systemd_service():
            return False
        
        # Start service
        if not self.start_service():
            return False
        
        # Check service status
        self.check_service_status()
        
        # Display completion message
        self.display_completion_message()
        
        return True
    
    def display_completion_message(self):
        """
        Display completion message with instructions.
        """
        print()
        print("Installation completed successfully!")
        print(f"The UnitAPI Remote Keyboard Server is now running on {self.host}:{self.server_port}")
        print()
        print("You can control it with the following commands:")
        print(f"  Start:   ssh {self.user}@{self.host} 'sudo systemctl start unitapi-keyboard.service'")
        print(f"  Stop:    ssh {self.user}@{self.host} 'sudo systemctl stop unitapi-keyboard.service'")
        print(f"  Restart: ssh {self.user}@{self.host} 'sudo systemctl restart unitapi-keyboard.service'")
        print(f"  Status:  ssh {self.user}@{self.host} 'sudo systemctl status unitapi-keyboard.service'")
        print()
        print("To use the remote keyboard control client, update your .env file with:")
        print(f"RPI_HOST={self.host}")
        print(f"RPI_USER={self.user}")
        print("RPI_PASSWORD=your_password")
        print()
        print("Then run: python examples/remote_keyboard_control.py")


def main():
    """
    Main function to parse arguments and install the UnitAPI Remote Keyboard Server.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Display banner
    print("==================================================")
    print("UnitAPI Remote Keyboard Server Installation Script")
    print("==================================================")
    print()
    
    # Get values from .env file
    rpi_host = os.getenv('RPI_HOST', '')
    rpi_user = os.getenv('RPI_USER', 'pi')
    rpi_password = os.getenv('RPI_PASSWORD', '')
    install_dir = os.getenv('INSTALL_DIR', '/home/pi/unitapi')
    server_port = int(os.getenv('SERVER_PORT', '7890'))
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Install UnitAPI Remote Keyboard Server on Raspberry Pi')
    parser.add_argument('--host', default=rpi_host, help='Raspberry Pi host address')
    parser.add_argument('--user', default=rpi_user, help='SSH username')
    parser.add_argument('--password', default=rpi_password, help='SSH password')
    parser.add_argument('--port', type=int, default=22, help='SSH port')
    parser.add_argument('--install-dir', default=install_dir, help='Installation directory on Raspberry Pi')
    parser.add_argument('--server-port', type=int, default=server_port, help='UnitAPI server port')
    parser.add_argument('--identity', help='Path to SSH identity file for key-based authentication')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check if host is provided
    if not args.host:
        print("Please provide the Raspberry Pi host address with --host")
        return 1
    
    # Check if password or identity file is provided
    if not args.password and not args.identity:
        print("Please provide either a password with --password or an identity file with --identity")
        return 1
    
    # Display installation details
    print(f"Installing UnitAPI Remote Keyboard Server on Raspberry Pi")
    print(f"Host: {args.host}")
    print(f"User: {args.user}")
    print(f"Installation directory: {args.install_dir}")
    print(f"Server port: {args.server_port}")
    print()
    
    # Create installer
    installer = RemoteKeyboardServerInstaller(
        host=args.host,
        user=args.user,
        password=args.password,
        port=args.port,
        install_dir=args.install_dir,
        server_port=args.server_port,
        identity_file=args.identity,
        verbose=args.verbose
    )
    
    # Install
    if installer.install():
        return 0
    else:
        print("Installation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
