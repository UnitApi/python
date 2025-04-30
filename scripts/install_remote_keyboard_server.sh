#!/bin/bash
# Install and configure the UnitAPI Remote Keyboard Server on a Raspberry Pi

set -e

# Default values
RPI_HOST=""
RPI_USER="pi"
RPI_PASSWORD=""
INSTALL_DIR="/home/pi/unitapi"
SERVER_PORT=7890

# Display banner
echo "=================================================="
echo "UnitAPI Remote Keyboard Server Installation Script"
echo "=================================================="
echo

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
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
      SERVER_PORT="$2"
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if host is provided
if [ -z "$RPI_HOST" ]; then
  echo "Please provide the Raspberry Pi host address with --host"
  exit 1
fi

# Check if password is provided
if [ -z "$RPI_PASSWORD" ]; then
  echo "Please provide the Raspberry Pi password with --password"
  exit 1
fi

echo "Installing UnitAPI Remote Keyboard Server on Raspberry Pi"
echo "Host: $RPI_HOST"
echo "User: $RPI_USER"
echo "Installation directory: $INSTALL_DIR"
echo "Server port: $SERVER_PORT"
echo

# Create installation directory structure
echo "Creating installation directory structure..."
ssh -o StrictHostKeyChecking=no $RPI_USER@$RPI_HOST "mkdir -p $INSTALL_DIR/examples"

# Copy necessary files
echo "Copying files to Raspberry Pi..."
scp examples/remote_keyboard_server.py $RPI_USER@$RPI_HOST:$INSTALL_DIR/examples/
scp examples/device_discovery.py $RPI_USER@$RPI_HOST:$INSTALL_DIR/examples/

# Install required packages
echo "Installing required packages on Raspberry Pi..."
ssh $RPI_USER@$RPI_HOST "sudo apt-get update && sudo apt-get install -y python3-pip python3-venv"

# Create virtual environment and install dependencies
echo "Setting up Python environment and installing dependencies..."
ssh $RPI_USER@$RPI_HOST "cd $INSTALL_DIR && python3 -m venv venv && source venv/bin/activate && pip install unitapi python-dotenv pyautogui"

# Create systemd service file
echo "Creating systemd service for UnitAPI Remote Keyboard Server..."
cat > /tmp/unitapi-keyboard.service << EOF
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

# Copy and enable the service
scp /tmp/unitapi-keyboard.service $RPI_USER@$RPI_HOST:/tmp/
ssh $RPI_USER@$RPI_HOST "sudo mv /tmp/unitapi-keyboard.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable unitapi-keyboard.service"

# Start the service
echo "Starting UnitAPI Remote Keyboard Server service..."
ssh $RPI_USER@$RPI_HOST "sudo systemctl start unitapi-keyboard.service"

# Check service status
echo "Checking service status..."
ssh $RPI_USER@$RPI_HOST "sudo systemctl status unitapi-keyboard.service"

echo
echo "Installation completed successfully!"
echo "The UnitAPI Remote Keyboard Server is now running on $RPI_HOST:$SERVER_PORT"
echo
echo "You can control it with the following commands:"
echo "  Start:   ssh $RPI_USER@$RPI_HOST 'sudo systemctl start unitapi-keyboard.service'"
echo "  Stop:    ssh $RPI_USER@$RPI_HOST 'sudo systemctl stop unitapi-keyboard.service'"
echo "  Restart: ssh $RPI_USER@$RPI_HOST 'sudo systemctl restart unitapi-keyboard.service'"
echo "  Status:  ssh $RPI_USER@$RPI_HOST 'sudo systemctl status unitapi-keyboard.service'"
echo
echo "To use the remote keyboard control client, update your .env file with:"
echo "RPI_HOST=$RPI_HOST"
echo "RPI_USER=$RPI_USER"
echo "RPI_PASSWORD=your_password"
echo
echo "Then run: python examples/remote_keyboard_control.py"
