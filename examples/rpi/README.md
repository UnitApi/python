# Raspberry Pi Examples for UnitAPI

This directory contains examples specifically designed for using UnitAPI with Raspberry Pi hardware. These examples demonstrate how to interact with various Raspberry Pi hardware components like GPIO pins, camera modules, microphones, speakers, and sensors.

## Directory Structure

The examples are organized by device type:

- **gpio/**: GPIO and sensor examples
  - `gpio_server.py`: Server for GPIO functionality
  - `gpio_client.py`: Client for controlling GPIO pins
  - `led_control.py`: Advanced LED control examples
  - `sensors.py`: Examples for various sensors (temperature, distance, etc.)

- **camera/**: Camera module examples
  - `camera_server.py`: Server for camera functionality
  - `camera_client.py`: Client for capturing images and videos

- **mic/**: Microphone examples
  - `microphone_server.py`: Server for microphone functionality
  - `microphone_client.py`: Client for recording audio and monitoring levels

- **speaker/**: Speaker examples
  - `speaker_server.py`: Server for speaker functionality
  - `speaker_client.py`: Client for audio playback and volume control

- **respeaker/**: ReSpeaker microphone array examples
  - `respeaker_server.py`: Server for ReSpeaker functionality
  - `respeaker_client.py`: Client for audio recording, direction of arrival, and LED control

## Prerequisites

- Raspberry Pi (any model with GPIO pins)
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- Required Python packages for specific examples:
  - For camera examples: `picamera` or `opencv-python`
  - For audio examples: `pyaudio`
  - For sensor examples: `Adafruit_DHT` (for DHT11/DHT22 sensors)
  - For ReSpeaker examples: `numpy`

## Server and Client Architecture

These examples follow a client-server architecture:

1. **Server**: Runs on the Raspberry Pi and exposes hardware functionality through UnitAPI
2. **Client**: Connects to the server and controls the hardware remotely

### Running the Servers

Before running any client examples, you need to start the corresponding server on your Raspberry Pi:

```bash
# Start the GPIO server
python gpio/gpio_server.py --host 0.0.0.0 --port 7890

# Start the Camera server
python camera/camera_server.py --host 0.0.0.0 --port 7890

# Start the Microphone server
python mic/microphone_server.py --host 0.0.0.0 --port 7890

# Start the Speaker server
python speaker/speaker_server.py --host 0.0.0.0 --port 7890

# Start the ReSpeaker server
python respeaker/respeaker_server.py --host 0.0.0.0 --port 7890
```

The servers will expose the hardware functionality through UnitAPI, making it available for client applications to connect.

## Examples Overview

### 1. GPIO Examples (gpio/)

#### Server (`gpio_server.py`)

Exposes GPIO functionality through UnitAPI:
- Registers a GPIO device with the UnitAPI server
- Handles commands for pin mode setting, digital read/write, and PWM control
- Provides a clean shutdown mechanism

**Usage:**
```bash
# Run on the Raspberry Pi
python gpio/gpio_server.py --host 0.0.0.0 --port 7890
```

#### Client (`gpio_client.py`)

Demonstrates basic GPIO pin control on Raspberry Pi, including:
- Setting pin modes (input/output)
- Digital read/write operations
- PWM (Pulse Width Modulation) control
- Blinking LEDs
- Fading LEDs using PWM

**Usage:**
```bash
# Connect to a local server
python gpio/gpio_client.py --led-pin 18 --demo blink

# Connect to a remote Raspberry Pi
python gpio/gpio_client.py --host 192.168.1.100 --port 7890 --led-pin 18 --demo blink
```

#### LED Control (`led_control.py`)

Advanced LED control examples for Raspberry Pi:
- Blinking individual LEDs
- Fading LEDs with PWM
- Creating LED patterns with multiple LEDs
- Controlling RGB LEDs

**Usage:**
```bash
# Connect to a local GPIO server
python gpio/led_control.py --demo rgb --rgb-mode fade --duration 10
```

#### Sensors (`sensors.py`)

Demonstrates interfacing with various sensors connected to Raspberry Pi GPIO:
- DHT11/DHT22 temperature and humidity sensors
- HC-SR04 ultrasonic distance sensors
- PIR motion sensors
- Multi-sensor monitoring

**Usage:**
```bash
# Connect to a local GPIO server
python gpio/sensors.py --demo dht --dht-pin 4 --dht-type DHT22
```

### 2. Camera Examples (camera/)

#### Server (`camera_server.py`)

Exposes Raspberry Pi Camera Module functionality through UnitAPI:
- Registers a camera device with the UnitAPI server
- Handles commands for image capture and video recording
- Supports various image effects and resolutions
- Falls back to a virtual camera if no physical camera is detected

**Usage:**
```bash
# Run on the Raspberry Pi
python camera/camera_server.py --host 0.0.0.0 --port 7890
```

#### Client (`camera_client.py`)

Demonstrates using the Raspberry Pi Camera Module with UnitAPI:
- Capturing still images
- Recording video
- Creating timelapse sequences
- Applying image effects

**Usage:**
```bash
# Connect to a local server
python camera/camera_client.py --demo image --resolution 1920x1080
```

### 3. Microphone Examples (mic/)

#### Server (`microphone_server.py`)

Exposes microphone functionality through UnitAPI:
- Registers a microphone device with the UnitAPI server
- Handles commands for audio recording and level monitoring
- Supports various audio formats and sample rates

**Usage:**
```bash
# Run on the Raspberry Pi
python mic/microphone_server.py --host 0.0.0.0 --port 7890
```

#### Client (`microphone_client.py`)

Demonstrates using the Raspberry Pi microphone with UnitAPI:
- Recording audio to WAV or MP3 files
- Monitoring audio levels
- Voice activity detection

**Usage:**
```bash
# Connect to a local server
python mic/microphone_client.py --demo record --duration 10
```

### 4. Speaker Examples (speaker/)

#### Server (`speaker_server.py`)

Exposes speaker functionality through UnitAPI:
- Registers a speaker device with the UnitAPI server
- Handles commands for audio playback and volume control
- Supports various audio formats

**Usage:**
```bash
# Run on the Raspberry Pi
python speaker/speaker_server.py --host 0.0.0.0 --port 7890
```

#### Client (`speaker_client.py`)

Demonstrates using the Raspberry Pi speaker with UnitAPI:
- Playing audio files
- Generating and playing tones
- Controlling system volume

**Usage:**
```bash
# Connect to a local server
python speaker/speaker_client.py --demo file --audio-file sample.wav
```

### 5. ReSpeaker Examples (respeaker/)

#### Server (`respeaker_server.py`)

Exposes ReSpeaker microphone array functionality through UnitAPI:
- Registers a ReSpeaker device with the UnitAPI server
- Handles commands for audio recording, direction of arrival, and LED control
- Supports the ReSpeaker 4-Mic Array for Raspberry Pi

**Usage:**
```bash
# Run on the Raspberry Pi
python respeaker/respeaker_server.py --host 0.0.0.0 --port 7890
```

#### Client (`respeaker_client.py`)

Demonstrates using the ReSpeaker microphone array with UnitAPI:
- Recording audio with beamforming
- Getting direction of arrival (DOA)
- Controlling the LED ring
- Voice localization demo

**Usage:**
```bash
# Connect to a local server
python respeaker/respeaker_client.py --demo voice --duration 30
```

## Hardware Requirements

### GPIO Examples
- Raspberry Pi with GPIO pins
- LEDs, resistors (220-330 ohm)
- Push buttons
- Sensors (DHT11/DHT22, HC-SR04, PIR) as needed

### Camera Examples
- Raspberry Pi Camera Module (any version)
- Or USB webcam compatible with Linux

### Microphone Examples
- USB microphone
- Or Raspberry Pi compatible audio HAT

### Speaker Examples
- USB speakers
- Or Raspberry Pi compatible audio HAT
- Or HDMI audio output

### ReSpeaker Examples
- ReSpeaker 4-Mic Array for Raspberry Pi
- Or ReSpeaker 2-Mic HAT

## Client-Server Communication

The client and server communicate using the UnitAPI protocol:

1. The server registers devices and command handlers
2. The client connects to the server and discovers available devices
3. The client sends commands to control the devices
4. The server executes the commands and returns the results

This architecture allows for:
- Remote control of Raspberry Pi hardware
- Multiple clients connecting to the same server
- Separation of hardware control logic from application logic

## GPIO Pin Numbering

These examples use the BCM (Broadcom) pin numbering scheme, not the physical pin numbers on the Raspberry Pi header. To convert between different numbering schemes, refer to a Raspberry Pi GPIO pinout diagram.

## Troubleshooting

1. **Permission Issues**: If you encounter permission errors when accessing hardware, try running the server with sudo:
   ```bash
   sudo python gpio/gpio_server.py
   ```

2. **Camera Not Detected**: Ensure the camera module is properly connected and enabled in raspi-config:
   ```bash
   sudo raspi-config
   ```
   Then navigate to "Interfacing Options" > "Camera" and enable it.

3. **Audio Issues**: If you have issues with audio input/output:
   ```bash
   # List audio devices
   arecord -l  # Input devices
   aplay -l    # Output devices
   
   # Test microphone recording
   arecord -d 5 -f cd test.wav
   
   # Test speaker playback
   aplay test.wav
   ```

4. **ReSpeaker Issues**: For ReSpeaker setup problems:
   ```bash
   # Check if ReSpeaker is detected
   lsusb
   
   # Install ReSpeaker drivers if needed
   git clone https://github.com/respeaker/seeed-voicecard
   cd seeed-voicecard
   sudo ./install.sh
   sudo reboot
   ```

5. **Server Connection Issues**: If the client cannot connect to the server, check:
   - The server is running and listening on the correct interface (0.0.0.0 for all interfaces)
   - The port is not blocked by a firewall
   - The host and port in the client match the server
   - Network connectivity between client and server

## Safety Warnings

- Be careful when connecting components to GPIO pins. Incorrect wiring can damage your Raspberry Pi.
- Always connect LEDs with appropriate resistors (typically 220-330 ohms) to prevent damage.
- For sensors that require 5V, make sure they have proper level shifting for the GPIO pins which operate at 3.3V.
