FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    openssh-client \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

# Create installation directory
RUN mkdir -p /opt/unitapi

# Set up Python virtual environment
RUN python3 -m venv /opt/unitapi/venv
ENV PATH="/opt/unitapi/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip wheel setuptools
RUN pip install numpy websockets

# Clone UnitAPI repository
WORKDIR /opt
RUN git clone https://github.com/UnitApi/UnitApi.git
WORKDIR /opt/UnitApi/python
RUN pip install -e .

# Copy the client script
COPY client.py /opt/unitapi/
COPY entrypoint.sh /opt/unitapi/

# Make scripts executable
RUN chmod +x /opt/unitapi/client.py /opt/unitapi/entrypoint.sh

# Create data directory
RUN mkdir -p /data

# Set entrypoint
ENTRYPOINT ["/opt/unitapi/entrypoint.sh"]
