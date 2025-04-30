# Raspberry Pi ReSpeaker Examples for UnitAPI

This directory contains examples for controlling a ReSpeaker microphone array on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a ReSpeaker server on the Raspberry Pi and control it remotely from a client application.

## Files

- `respeaker_server.py`: Server that runs on the Raspberry Pi and exposes ReSpeaker functionality through UnitAPI
- `respeaker_client.py`: Client that connects to the server and controls the ReSpeaker microphone array

## Prerequisites

- Raspberry Pi (any model)
- ReSpeaker 4-Mic Array for Raspberry Pi or ReSpeaker 2-Mic HAT
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- ReSpeaker drivers and libraries installed
- NumPy installed (`pip install numpy`)

## ReSpeaker Setup

Before using these examples, you need to install the ReSpeaker drivers and libraries:

```bash
# Clone the ReSpeaker drivers repository
git clone https://github.com/respeaker/seeed-voicecard
cd seeed-voicecard

# Install the drivers
sudo ./install.sh
sudo reboot

# Install the ReSpeaker Python library
pip install respeaker
```

## Server Setup

The ReSpeaker server runs on the Raspberry Pi and exposes ReSpeaker functionality through UnitAPI. It registers a ReSpeaker device with the UnitAPI server and handles commands for audio recording, direction of arrival (DOA), and LED control.

### Running the Server

```bash
# Run on the Raspberry Pi
python respeaker_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--model`: ReSpeaker model (choices: 4mic, 2mic) (default: 4mic)

## Client Usage

The ReSpeaker client connects to the server and controls the ReSpeaker microphone array remotely. It provides methods for recording audio with beamforming, getting direction of arrival (DOA), and controlling the LED ring.

### Running the Client

```bash
# Connect to a local server
python respeaker_client.py --demo voice --duration 30

# Connect to a remote Raspberry Pi
python respeaker_client.py --host 192.168.1.100 --port 7890 --demo doa
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: voice, doa, led, all)
- `--duration`: Duration of the demo in seconds (default: 30)
- `--output`: Output file path for audio recording
- `--sample-rate`: Audio sample rate in Hz (default: 16000)
- `--channels`: Number of audio channels (default: 1)
- `--format`: Audio format (choices: wav, mp3) (default: wav)

## Demo Modes

The client provides several demo modes:

1. **Voice Demo** (`--demo voice`): Records audio with beamforming and saves it to a file
2. **Direction of Arrival Demo** (`--demo doa`): Continuously displays the direction of sound sources
3. **LED Demo** (`--demo led`): Demonstrates various LED patterns on the ReSpeaker's LED ring
4. **All Demos** (`--demo all`): Runs all demos in sequence

## Supported ReSpeaker Operations

The ReSpeaker examples support the following operations:

- **Audio Recording with Beamforming**: Record audio with enhanced directional sensitivity
- **Direction of Arrival (DOA)**: Determine the direction of sound sources
- **LED Control**: Control the LED ring on the ReSpeaker 4-Mic Array
- **Voice Localization**: Visualize the direction of voice sources

## ReSpeaker Models

These examples support the following ReSpeaker models:

- **ReSpeaker 4-Mic Array for Raspberry Pi**: Features 4 microphones and an LED ring
- **ReSpeaker 2-Mic HAT**: Features 2 microphones and 3 LEDs

## Troubleshooting

1. **ReSpeaker Not Detected**: Ensure the ReSpeaker is properly connected and the drivers are installed:
   ```bash
   # Check if ReSpeaker is detected
   arecord -l
   ```

2. **Driver Installation Issues**: If you have trouble installing the drivers, try:
   ```bash
   # Update your system first
   sudo apt-get update
   sudo apt-get upgrade
   
   # Then reinstall the drivers
   cd seeed-voicecard
   sudo ./install.sh
   sudo reboot
   ```

3. **LED Control Issues**: If the LEDs don't work, check if the SPI interface is enabled:
   ```bash
   # Enable SPI interface
   sudo raspi-config
   # Navigate to "Interfacing Options" > "SPI" and enable it
   ```

4. **Audio Quality Issues**: If you experience poor audio quality, try adjusting the microphone gain or using a different beamforming algorithm.

5. **Connection Issues**: Ensure the server is running and accessible from the client's network.

## Example Use Cases

1. **Voice Assistant**: Create a voice-controlled assistant with directional awareness
2. **Sound Localization**: Determine the direction of sound sources in a room
3. **Interactive LED Feedback**: Provide visual feedback through the LED ring based on sound direction
4. **Multi-Room Audio**: Create a distributed audio recording system with multiple ReSpeakers
5. **Conference Room System**: Build a smart conference room system with directional audio recording
