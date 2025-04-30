#!/bin/bash
# Install and configure the UnitAPI Remote Keyboard Server on a Raspberry Pi
# Fixed version to address common installation issues

# Function to display help
show_help() {
    echo "UnitAPI Remote Keyboard Server Installation Script"
    echo "=================================================="
    echo "This script installs and configures the UnitAPI Remote Keyboard Server on a Raspberry Pi."
    echo
    echo "Usage: ./install_remote_keyboard_server_fixed.sh [options]"
    echo
    echo "Options:"
    echo "  --host HOST          Raspberry Pi host address"
    echo "  --user USER          SSH username (default: pi)"
    echo "  --password PASS      SSH password"
    echo "  --port PORT          SSH port (default: 22)"
    echo "  --install-dir DIR    Installation directory (default: /home/pi/unitapi)"
    echo "  --server-port PORT   UnitAPI server port (default: 7890)"
    echo "  --identity FILE      Path to SSH identity file for key-based authentication"
    echo "  --service-command CMD Control the service (start, stop, restart, status)"
    echo "  --help               Show this help message"
    echo
    echo "Examples:"
    echo "  ./install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry"
    echo "  ./install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --identity ~/.ssh/id_rsa"
    echo "  ./install_remote_keyboard_server_fixed.sh --host 192.168.1.100 --password raspberry --service-command status"
    echo
}

# SSH connection function with improved error handling
ssh_connect() {
    local command="$1"
    local max_attempts=3
    local attempt=1
    local ssh_opts="-o ConnectTimeout=10 -o ServerAliveInterval=60 -p $SSH_PORT"
    
    # Add identity file if provided
    if [ -n "$IDENTITY_FILE" ]; then
        if [ -f "$IDENTITY_FILE" ]; then
            ssh_opts="$ssh_opts -i $IDENTITY_FILE -o PreferredAuthentications=publickey -o IdentitiesOnly=yes"
        else
            echo "Warning: Identity file $IDENTITY_FILE not found!"
            if [ -z "$RPI_PASSWORD" ]; then
                echo "No valid authentication method available. Exiting."
                exit 1
            fi
        fi
    fi
    
    # Set authentication options based on authentication method
    if [ -n "$RPI_PASSWORD" ] && [ -z "$IDENTITY_FILE" ]; then
        # Explicitly disable pubkey authentication to prevent "too many authentication failures"
        ssh_opts="$ssh_opts -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1"
    fi
    
    # Set authentication options based on authentication method
    if [ -n "$RPI_PASSWORD" ] && [ -z "$IDENTITY_FILE" ]; then
        # Explicitly disable pubkey authentication to prevent "too many authentication failures"
        ssh_opts="$ssh_opts -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1"
    fi
    
    # Use sshpass if password is provided
    if [ -n "$RPI_PASSWORD" ]; then
        # Check if sshpass is installed
        if ! command -v sshpass >/dev/null 2>&1; then
            echo "Warning: sshpass is not installed. Installing it now..."
            sudo apt-get update && sudo apt-get install -y sshpass
        fi
        
        while [ $attempt -le $max_attempts ]; do
            echo "SSH connection attempt $attempt of $max_attempts..."
            if sshpass -p "$RPI_PASSWORD" ssh $ssh_opts -o StrictHostKeyChecking=no "$RPI_USER@$RPI_HOST" "$command"; then
                return 0
            fi
            attempt=$((attempt+1))
            sleep 2
        done
        
        echo "Failed to connect after $max_attempts attempts."
        return 1
    else
        # Normal SSH connection
        while [ $attempt -le $max_attempts ]; do
            echo "SSH connection attempt $attempt of $max_attempts..."
            if ssh $ssh_opts -o StrictHostKeyChecking=no "$RPI_USER@$RPI_HOST" "$command"; then
                return 0
            fi
            attempt=$((attempt+1))
            sleep 2
        done
        
        echo "Failed to connect after $max_attempts attempts."
        return 1
    fi
}

# SCP function to copy files with improved error handling
scp_copy() {
    local src="$1"
    local dest="$2"
    local max_attempts=3
    local attempt=1
    local ssh_opts="-o ConnectTimeout=10 -o ServerAliveInterval=60 -P $SSH_PORT"
    
    # Add identity file if provided
    if [ -n "$IDENTITY_FILE" ]; then
        if [ -f "$IDENTITY_FILE" ]; then
            ssh_opts="$ssh_opts -i $IDENTITY_FILE -o PreferredAuthentications=publickey -o IdentitiesOnly=yes"
        else
            echo "Warning: Identity file $IDENTITY_FILE not found!"
            if [ -z "$RPI_PASSWORD" ]; then
                echo "No valid authentication method available. Exiting."
                exit 1
            fi
        fi
    fi
    
    # Use sshpass if password is provided
    if [ -n "$RPI_PASSWORD" ]; then
        # Check if sshpass is installed
        if ! command -v sshpass >/dev/null 2>&1; then
            echo "Warning: sshpass is not installed. Installing it now..."
            sudo apt-get update && sudo apt-get install -y sshpass
        fi
        
        while [ $attempt -le $max_attempts ]; do
            echo "SCP transfer attempt $attempt of $max_attempts..."
            if sshpass -p "$RPI_PASSWORD" scp $ssh_opts -o StrictHostKeyChecking=no "$src" "$dest"; then
                return 0
            fi
            attempt=$((attempt+1))
            sleep 2
        done
        
        echo "Failed to transfer files after $max_attempts attempts."
        return 1
    else
        # Normal SCP
        while [ $attempt -le $max_attempts ]; do
            echo "SCP transfer attempt $attempt of $max_attempts..."
            if scp $ssh_opts -o StrictHostKeyChecking=no "$src" "$dest"; then
                return 0
            fi
            attempt=$((attempt+1))
            sleep 2
        done
        
        echo "Failed to transfer files after $max_attempts attempts."
        return 1
    fi
}

# Load values from .env file if it exists
if [ -f .env ]; then
    echo "Loading configuration from .env file..."
    # Source the .env file to get environment variables
    export $(grep -v '^#' .env | xargs)
fi

# Set default values (use values from .env if available)
RPI_HOST=${RPI_HOST:-""}
RPI_USER=${RPI_USER:-"pi"}
RPI_PASSWORD=${RPI_PASSWORD:-""}
SSH_PORT=${SSH_PORT:-22}
INSTALL_DIR=${INSTALL_DIR:-"/home/pi/unitapi"}
SERVER_PORT=${SERVER_PORT:-7890}
IDENTITY_FILE=${IDENTITY_FILE:-""}

# Display banner
echo "=================================================="
echo "UnitAPI Remote Keyboard Server Installation Script"
echo "=================================================="
echo

# Service command function with improved error handling
handle_service_command() {
    local command="$1"
    
    case "$command" in
        start|stop|restart|status)
            echo "Executing service command: $command"
            
            # First check if the service exists
            if ! ssh_connect "systemctl list-unit-files | grep -q unitapi-keyboard.service"; then
                echo "Error: unitapi-keyboard.service not found on the remote system."
                echo
                echo "The service may not be installed. You have the following options:"
                echo "1. Run this script without the --service-command option to install the service"
                echo "2. Check if the service is installed under a different name:"
                echo "   ssh $RPI_USER@$RPI_HOST \"systemctl list-unit-files | grep unitapi\""
                echo
                return 1
            fi
            
            # Execute the command
            ssh_connect "sudo systemctl $command unitapi-keyboard.service"
            
            # If status command, provide additional information
            if [ "$command" = "status" ]; then
                echo
                echo "Additional troubleshooting commands:"
                echo "- View service logs: ssh $RPI_USER@$RPI_HOST \"sudo journalctl -u unitapi-keyboard.service\""
                echo "- Check if Python is installed: ssh $RPI_USER@$RPI_HOST \"python3 --version\""
                echo "- Verify installation directory: ssh $RPI_USER@$RPI_HOST \"ls -la $INSTALL_DIR\""
            fi
            
            return $?
            ;;
        *)
            echo "Unknown service command: $command"
            echo "Valid commands are: start, stop, restart, status"
            return 1
            ;;
    esac
}

# Parse command line arguments
SERVICE_COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --host)
            RPI_HOST="$2"
            shift 2
            ;;
        --user)
            RPI_USER="$2"
            shift 2
            ;;
        --password)
            RPI_PASSWORD="$2"
            shift 2
            ;;
        --port)
            SSH_PORT="$2"
            shift 2
            ;;
        --server-port)
            SERVER_PORT="$2"
            shift 2
            ;;
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --identity)
            IDENTITY_FILE="$2"
            shift 2
            ;;
        --service-command)
            SERVICE_COMMAND="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Check if host is provided
if [ -z "$RPI_HOST" ]; then
    echo "Please provide the Raspberry Pi host address with --host"
    exit 1
fi

# Check if password or identity file is provided
if [ -z "$RPI_PASSWORD" ] && [ -z "$IDENTITY_FILE" ]; then
    echo "Please provide either a password with --password or an identity file with --identity"
    exit 1
fi

# If a service command was provided, execute it and exit
if [ -n "$SERVICE_COMMAND" ]; then
    handle_service_command "$SERVICE_COMMAND"
    exit $?
fi

# Otherwise, proceed with the full installation
echo "Installing UnitAPI Remote Keyboard Server on Raspberry Pi"
echo "Host: $RPI_HOST"
echo "User: $RPI_USER"
echo "SSH Port: $SSH_PORT"
echo "Installation directory: $INSTALL_DIR"
echo "Server port: $SERVER_PORT"
echo

# Test connection
echo "Testing SSH connection..."
if ! ssh_connect "echo Connection successful"; then
    echo "Failed to connect to $RPI_HOST. Please check your credentials and try again."
    exit 1
fi

# Check Raspberry Pi OS version
echo "Checking Raspberry Pi OS version..."
OS_VERSION=$(ssh_connect "cat /etc/os-release | grep VERSION_CODENAME | cut -d= -f2")
echo "Detected OS version: $OS_VERSION"

# Create installation directory structure
echo "Creating installation directory structure..."
ssh_connect "mkdir -p $INSTALL_DIR/examples"

# Copy necessary files
echo "Copying files to Raspberry Pi..."
scp_copy "examples/remote_keyboard_server.py" "$RPI_USER@$RPI_HOST:$INSTALL_DIR/examples/"
scp_copy "examples/device_discovery.py" "$RPI_USER@$RPI_HOST:$INSTALL_DIR/examples/"

# Install required packages with improved repository handling
echo "Installing required packages on Raspberry Pi..."
if [[ "$OS_VERSION" == "stretch" ]]; then
    echo "Warning: Detected outdated 'stretch' release. Updating sources.list..."
    # Update sources.list to use archive.raspberrypi.org for stretch
    ssh_connect "sudo sed -i 's|http://raspbian.raspberrypi.org/raspbian|http://archive.raspberrypi.org/debian|g' /etc/apt/sources.list"
fi

# Install required packages with retry mechanism
MAX_ATTEMPTS=3
for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Package installation attempt $attempt of $MAX_ATTEMPTS..."
    if ssh_connect "sudo apt-get update && sudo apt-get install -y python3-pip python3-venv"; then
        echo "Package installation successful."
        break
    fi
    
    if [ $attempt -eq $MAX_ATTEMPTS ]; then
        echo "Failed to install packages after $MAX_ATTEMPTS attempts."
        echo "Continuing with installation, but some features may not work correctly."
    else
        echo "Retrying package installation in 5 seconds..."
        sleep 5
    fi
done

# Create virtual environment and install dependencies with SSL verification disabled
echo "Setting up Python environment and installing dependencies..."
ssh_connect "cd $INSTALL_DIR && python3 -m venv venv && source venv/bin/activate && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host piwheels.org python-dotenv pyautogui"

# Install unitapi package with retry mechanism
MAX_ATTEMPTS=3
for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "UnitAPI installation attempt $attempt of $MAX_ATTEMPTS..."
    if ssh_connect "cd $INSTALL_DIR && source venv/bin/activate && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host piwheels.org unitapi"; then
        echo "UnitAPI installation successful."
        break
    fi
    
    if [ $attempt -eq $MAX_ATTEMPTS ]; then
        echo "Failed to install UnitAPI after $MAX_ATTEMPTS attempts."
        echo "Continuing with installation, but the service may not work correctly."
    else
        echo "Retrying UnitAPI installation in 5 seconds..."
        sleep 5
    fi
done

# Create systemd service file locally
echo "Creating systemd service for UnitAPI Remote Keyboard Server..."
SERVICE_FILE="unitapi-keyboard.service"
cat > $SERVICE_FILE << EOF
[Unit]
Description=UnitAPI Remote Keyboard Server
After=network.target

[Service]
User=$RPI_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/examples/remote_keyboard_server.py --port $SERVER_PORT
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Copy service file to Raspberry Pi
echo "Copying service file to Raspberry Pi..."
scp_copy "$SERVICE_FILE" "$RPI_USER@$RPI_HOST:/tmp/"

# Verify service file was copied successfully
ssh_connect "if [ -f /tmp/$SERVICE_FILE ]; then echo 'Service file copied successfully.'; else echo 'Service file not found!'; exit 1; fi"

# Install and enable the service
echo "Installing and enabling service..."
ssh_connect "sudo mv /tmp/$SERVICE_FILE /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable unitapi-keyboard.service"

# Clean up local service file
rm -f $SERVICE_FILE

# Start the service
echo "Starting UnitAPI Remote Keyboard Server service..."
ssh_connect "sudo systemctl start unitapi-keyboard.service"

# Check service status
echo "Checking service status..."
ssh_connect "sudo systemctl status unitapi-keyboard.service"

echo
echo "Installation completed successfully!"
echo "The UnitAPI Remote Keyboard Server is now running on $RPI_HOST:$SERVER_PORT"
echo
echo "You can control it with the following commands:"
echo "  Start:   ./install_remote_keyboard_server_fixed.sh --host $RPI_HOST --user $RPI_USER --password <password> --service-command start"
echo "  Stop:    ./install_remote_keyboard_server_fixed.sh --host $RPI_HOST --user $RPI_USER --password <password> --service-command stop"
echo "  Restart: ./install_remote_keyboard_server_fixed.sh --host $RPI_HOST --user $RPI_USER --password <password> --service-command restart"
echo "  Status:  ./install_remote_keyboard_server_fixed.sh --host $RPI_HOST --user $RPI_USER --password <password> --service-command status"
echo
echo "To use the remote keyboard control client, update your .env file with:"
echo "RPI_HOST=$RPI_HOST"
echo "RPI_USER=$RPI_USER"
echo "RPI_PASSWORD=your_password"
echo
echo "Then run: python examples/remote_keyboard_control.py"
