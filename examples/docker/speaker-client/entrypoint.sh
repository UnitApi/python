#!/bin/bash
# Entrypoint script for the UnitAPI Speaker Client container

# Wait for the server to be ready
echo "Waiting for the speaker server to be ready..."
sleep 5

# Set server host and port from environment variables
SERVER_HOST=${SERVER_HOST:-172.28.1.2}
SERVER_PORT=${SERVER_PORT:-7890}

# Copy the SSH installation script
cp /opt/UnitApi/python/scripts/install_remote_speaker_agent_via_ssh.sh /opt/unitapi/

# Make it executable
chmod +x /opt/unitapi/install_remote_speaker_agent_via_ssh.sh

# Install the speaker agent on the server using SSH
echo "Installing speaker agent on the server using SSH..."
echo "This may take a few minutes..."
sshpass -p "unitapi" /opt/unitapi/install_remote_speaker_agent_via_ssh.sh $SERVER_HOST root

# Start the client script
echo "Starting the speaker client..."
python3 /opt/unitapi/client.py --host $SERVER_HOST --port $SERVER_PORT

# Keep the container running
echo "UnitAPI Speaker Client is ready"
echo "Server host: $SERVER_HOST"
echo "Server port: $SERVER_PORT"

# Start an interactive shell
exec /bin/bash
