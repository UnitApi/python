# Raspberry Pi Examples for UnitAPI

This directory contains examples specifically designed for using UnitAPI with Raspberry Pi hardware. These examples demonstrate how to interact with various Raspberry Pi hardware components like GPIO pins, camera modules, and sensors.

## Prerequisites

- Raspberry Pi (any model with GPIO pins)
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- Required Python packages for specific examples:
  - For camera examples: `picamera` or `opencv-python`
  - For sensor examples: `Adafruit_DHT` (for DHT11/DHT22 sensors)
  - For LED examples: No additional packages required

## Examples Overview

### 1. GPIO Control (`gpio_control.py`)

Demonstrates basic GPIO pin control on Raspberry Pi, including:
- Setting pin modes (input/output)
- Digital read/write operations
- PWM (Pulse Width Modulation) control
- Blinking LEDs
- Fading LEDs using PWM

**Usage:**
```bash
python gpio_control.py --led-pin 18 --demo blink
```

**Options:**
- `--led-pin`: GPIO pin number for LED (BCM numbering)
- `--demo`: Demo to run (blink, fade, button, or all)
- `--debug`: Enable debug logging

### 2. Camera Module (`camera_module.py`)

Demonstrates using the Raspberry Pi Camera Module with UnitAPI:
- Capturing still images
- Recording video
- Creating timelapse sequences
- Applying image effects

**Usage:**
```bash
python camera_module.py --demo image --resolution 1920x1080
```

**Options:**
- `--demo`: Demo to run (image, video, timelapse, effect)
- `--resolution`: Image/video resolution (WxH)
- `--output`: Output file or directory
- `--duration`: Video duration in seconds (for video demo)
- `--effect`: Image effect to apply (for effect demo)

### 3. Sensors (`sensors.py`)

Demonstrates interfacing with various sensors connected to Raspberry Pi GPIO:
- DHT11/DHT22 temperature and humidity sensors
- HC-SR04 ultrasonic distance sensors
- PIR motion sensors
- Multi-sensor monitoring

**Usage:**
```bash
python sensors.py --demo dht --dht-pin 4 --dht-type DHT22
```

**Options:**
- `--demo`: Demo to run (dht, ultrasonic, pir, multi)
- `--dht-pin`: GPIO pin for DHT sensor data
- `--dht-type`: DHT sensor type (DHT11 or DHT22)
- `--trigger-pin`: GPIO pin for ultrasonic trigger
- `--echo-pin`: GPIO pin for ultrasonic echo
- `--pir-pin`: GPIO pin for PIR motion sensor
- `--duration`: Monitoring duration in seconds
- `--output`: Output file to save readings (JSON format)

### 4. LED Control (`led_control.py`)

Advanced LED control examples for Raspberry Pi:
- Blinking individual LEDs
- Fading LEDs with PWM
- Creating LED patterns with multiple LEDs
- Controlling RGB LEDs

**Usage:**
```bash
python led_control.py --demo rgb --rgb-mode fade --duration 10
```

**Options:**
- `--demo`: Demo to run (blink, fade, pulse, pattern, rgb, all)
- `--led-pin`: GPIO pin for single LED
- `--led-pins`: Comma-separated GPIO pins for multiple LEDs
- `--red-pin`: GPIO pin for RGB red channel
- `--green-pin`: GPIO pin for RGB green channel
- `--blue-pin`: GPIO pin for RGB blue channel
- `--pattern`: LED pattern type (chase, alternate, flash, random)
- `--rgb-mode`: RGB LED control mode (cycle, random, fade)
- `--duration`: Demo duration in seconds

## GPIO Pin Numbering

These examples use the BCM (Broadcom) pin numbering scheme, not the physical pin numbers on the Raspberry Pi header. To convert between different numbering schemes, refer to a Raspberry Pi GPIO pinout diagram.

## Notes for Specific Raspberry Pi Models

### Raspberry Pi Zero / Zero W
- All examples should work, but camera examples require the camera module to be connected properly
- Limited processing power may affect performance of video recording

### Raspberry Pi 3 / 4
- All examples should work at full performance
- Multiple examples can be run simultaneously

### Raspberry Pi Pico
- These examples are not designed for Raspberry Pi Pico, which uses a different architecture

## Troubleshooting

1. **Permission Issues**: If you encounter permission errors when accessing GPIO pins, try running the examples with sudo:
   ```bash
   sudo python gpio_control.py
   ```

2. **Camera Not Detected**: Ensure the camera module is properly connected and enabled in raspi-config:
   ```bash
   sudo raspi-config
   ```
   Then navigate to "Interfacing Options" > "Camera" and enable it.

3. **GPIO Pin Conflicts**: Make sure the GPIO pins you're using aren't being used by other processes. You can check the current state of GPIO pins with:
   ```bash
   gpio readall
   ```

4. **UnitAPI Server Connection**: Ensure the UnitAPI server is running before executing these examples. If connecting to a remote server, specify the host and port:
   ```bash
   python gpio_control.py --host 192.168.1.100 --port 7890
   ```

## Safety Warnings

- Be careful when connecting components to GPIO pins. Incorrect wiring can damage your Raspberry Pi.
- Always connect LEDs with appropriate resistors (typically 220-330 ohms) to prevent damage.
- For sensors that require 5V, make sure they have proper level shifting for the GPIO pins which operate at 3.3V.
