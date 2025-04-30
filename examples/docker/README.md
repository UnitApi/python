# UnitAPI Docker Example: Remote Speaker Agent

This example demonstrates how to set up a virtual speaker server on one machine (PC1) and a client on another machine (PC2) using Docker Compose. The client will install the UnitAPI speaker agent on the server using SSH and then connect to it to control the virtual speakers.

## Overview

This Docker Compose setup creates two containers:

1. **speaker-server**: A container that runs virtual speakers and exposes them through the UnitAPI protocol.
2. **speaker-client**: A container that connects to the speaker server, installs the UnitAPI speaker agent using SSH, and provides a client interface to control the speakers.

This setup simulates a real-world scenario where you have a remote PC with speakers that you want to control from another PC.

## Prerequisites

- Docker and Docker Compose installed on your machine
- Basic knowledge of Docker and Docker Compose
- Understanding of the UnitAPI speaker agent

## Directory Structure

```
docker/
├── docker-compose.yml         # Docker Compose configuration
├── README.md                  # This file
├── speaker-server/            # Server container files
│   ├── Dockerfile             # Server container definition
│   ├── entrypoint.sh          # Server startup script
│   ├── virtual_speaker.py     # Virtual speaker implementation
│   └── data/                  # Shared volume for server data
└── speaker-client/            # Client container files
    ├── Dockerfile             # Client container definition
    ├── entrypoint.sh          # Client startup script
    ├── client.py              # Speaker client implementation
    └── data/                  # Shared volume for client data
```

## How It Works

1. The `speaker-server` container creates virtual speakers and exposes them through the UnitAPI protocol.
2. The `speaker-client` container connects to the server via SSH and installs the UnitAPI speaker agent.
3. The client then connects to the server's UnitAPI interface to control the virtual speakers.

This simulates the process of installing the UnitAPI speaker agent on a remote PC and controlling its speakers.

## Usage

### Starting the Containers

```bash
# Navigate to the docker directory
cd examples/docker

# Start the containers
docker-compose up -d

# View the logs
docker-compose logs -f
```

### Accessing the Client Container

```bash
# Access the client container shell
docker exec -it unitapi-speaker-client bash

# Inside the container, you can use the client script
python /opt/unitapi/client.py --host 172.28.1.2 --list
python /opt/unitapi/client.py --host 172.28.1.2 --test
```

### Accessing the Server Container

```bash
# Access the server container shell
docker exec -it unitapi-speaker-server bash

# Inside the container, you can check the speaker agent status
unitapi-speaker --status
unitapi-speaker --list
```

### Stopping the Containers

```bash
# Stop the containers
docker-compose down
```

## Customization

You can customize the setup by modifying the following files:

- `docker-compose.yml`: Change the network configuration, port mappings, etc.
- `speaker-server/virtual_speaker.py`: Modify the virtual speaker implementation.
- `speaker-client/client.py`: Customize the client behavior.

### Environment Variables

The Docker Compose setup supports the following environment variables:

- `VIRTUAL_SPEAKERS`: Number of virtual speakers to create on the server (default: 2)
- `SERVER_HOST`: Hostname or IP address of the server (default: 172.28.1.2)
- `SERVER_PORT`: Port number of the UnitAPI server (default: 7890)

You can set these variables in the `docker-compose.yml` file or pass them when starting the containers:

```bash
VIRTUAL_SPEAKERS=4 docker-compose up -d
```

## Testing the Setup

Once the containers are running, you can test the setup by:

1. Listing the available speakers:
   ```bash
   docker exec -it unitapi-speaker-client python /opt/unitapi/client.py --host 172.28.1.2 --list
   ```

2. Testing all speakers:
   ```bash
   docker exec -it unitapi-speaker-client python /opt/unitapi/client.py --host 172.28.1.2 --test
   ```

3. Testing a specific speaker:
   ```bash
   docker exec -it unitapi-speaker-client python /opt/unitapi/client.py --host 172.28.1.2 --device virtual_speaker_1
   ```

4. Monitoring the speakers:
   ```bash
   docker exec -it unitapi-speaker-client python /opt/unitapi/client.py --host 172.28.1.2 --monitor --interval 30
   ```

## Troubleshooting

If you encounter issues with the setup, check the following:

1. Make sure the containers are running:
   ```bash
   docker-compose ps
   ```

2. Check the container logs:
   ```bash
   docker-compose logs -f
   ```

3. Verify the network connectivity between the containers:
   ```bash
   docker exec -it unitapi-speaker-client ping 172.28.1.2
   ```

4. Check if the SSH server is running on the server container:
   ```bash
   docker exec -it unitapi-speaker-server service ssh status
   ```

5. Verify the UnitAPI server is running on the server container:
   ```bash
   docker exec -it unitapi-speaker-server ps aux | grep unitapi
   ```

## Extending the Example

You can extend this example to include more features:

1. Add more virtual speakers by changing the `VIRTUAL_SPEAKERS` environment variable.
2. Implement a web interface for controlling the speakers.
3. Add support for playing audio files from the client to the server.
4. Integrate with other UnitAPI devices like microphones or cameras.

## Conclusion

This Docker example demonstrates how to use the UnitAPI speaker agent to control speakers on a remote machine. It shows the process of installing the agent via SSH and then using it to control the speakers. This can be used as a starting point for building more complex applications that involve remote audio control.
