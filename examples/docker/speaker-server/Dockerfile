FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    openssh-server \
    sudo \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH
RUN mkdir /var/run/sshd
RUN echo 'root:unitapi' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create installation directory
RUN mkdir -p /opt/unitapi

# Set up Python virtual environment
RUN python3 -m venv /opt/unitapi/venv
ENV PATH="/opt/unitapi/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip wheel setuptools
RUN pip install pyaudio websockets numpy sounddevice soundfile

# Clone UnitAPI repository
WORKDIR /opt
RUN git clone https://github.com/UnitApi/UnitApi.git
WORKDIR /opt/UnitApi/python
RUN pip install -e .

# Copy the virtual speaker script
COPY virtual_speaker.py /opt/unitapi/
COPY entrypoint.sh /opt/unitapi/

# Make scripts executable
RUN chmod +x /opt/unitapi/virtual_speaker.py /opt/unitapi/entrypoint.sh

# Create data directory
RUN mkdir -p /data

# Expose ports
EXPOSE 7890 8765 22

# Set entrypoint
ENTRYPOINT ["/opt/unitapi/entrypoint.sh"]
