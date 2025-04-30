#!/bin/bash
# Entrypoint script for the UnitAPI Speaker Server container

# Start SSH server
service ssh start
echo "SSH server started"

# Copy the installation script to the correct location
cp /opt/UnitApi/python/scripts/install_remote_speaker_agent.sh /opt/unitapi/

# Make it executable
chmod +x /opt/unitapi/install_remote_speaker_agent.sh

# Start the virtual speaker service
echo "Starting virtual speaker service with ${VIRTUAL_SPEAKERS:-1} speakers"
python3 /opt/unitapi/virtual_speaker.py --num-speakers ${VIRTUAL_SPEAKERS:-1} &

# Keep the container running
echo "UnitAPI Speaker Server is ready"
echo "SSH credentials: root:unitapi"
echo "UnitAPI server running on port 7890"
echo "WebSocket server running on port 8765"

# Keep the container running
tail -f /dev/null
