# Raspberry Pi GPIO Examples for UnitAPI

This directory contains examples for controlling GPIO pins on a Raspberry Pi using UnitAPI. These examples demonstrate how to set up a GPIO server on the Raspberry Pi and control it remotely from a client application.

## Files

- `gpio_server.py`: Server that runs on the Raspberry Pi and exposes GPIO functionality through UnitAPI
- `gpio_client.py`: Client that connects to the server and controls GPIO pins
- `led_control.py`: Advanced LED control examples (blinking, fading, patterns)
- `sensors.py`: Examples for interfacing with various sensors (temperature, distance, motion)

## Prerequisites

- Raspberry Pi (any model with GPIO pins)
- Python 3.7 or higher
- UnitAPI installed (`pip install unitapi`)
- RPi.GPIO or gpiozero package installed
- Basic electronic components (LEDs, resistors, sensors, etc.)

## Server Setup

The GPIO server runs on the Raspberry Pi and exposes GPIO functionality through UnitAPI. It registers a GPIO device with the UnitAPI server and handles commands for pin mode setting, digital read/write, and PWM control.

### Running the Server

```bash
# Run on the Raspberry Pi
python gpio_server.py --host 0.0.0.0 --port 7890
```

Options:
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 7890)
- `--debug`: Enable debug logging
- `--pin-mode`: Default pin numbering mode (choices: BCM, BOARD) (default: BCM)

## Client Usage

The GPIO client connects to the server and controls the GPIO pins remotely. It provides methods for setting pin modes, reading and writing pin values, and controlling PWM.

### Running the GPIO Control Client

```bash
# Connect to a local server
python gpio_client.py --led-pin 18 --demo blink

# Connect to a remote Raspberry Pi
python gpio_client.py --host 192.168.1.100 --port 7890 --led-pin 18 --demo blink
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--led-pin`: GPIO pin number for LED (default: 18)
- `--button-pin`: GPIO pin number for button (default: 17)
- `--demo`: Demo to run (choices: blink, fade, button, pwm)

### Running the LED Control Client

```bash
# Connect to a local server
python led_control.py --demo rgb --rgb-mode fade --duration 10

# Connect to a remote Raspberry Pi
python led_control.py --host 192.168.1.100 --port 7890 --demo pattern
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: blink, fade, pattern, rgb)
- `--led-pins`: Comma-separated list of GPIO pins for LEDs (default: 18,23,24)
- `--rgb-pins`: Comma-separated list of GPIO pins for RGB LED (R,G,B) (default: 17,27,22)
- `--rgb-mode`: RGB LED mode (choices: solid, blink, fade, cycle) (default: cycle)
- `--duration`: Duration of the demo in seconds (default: 30)

### Running the Sensors Client

```bash
# Connect to a local server
python sensors.py --demo dht --dht-pin 4 --dht-type DHT22

# Connect to a remote Raspberry Pi
python sensors.py --host 192.168.1.100 --port 7890 --demo ultrasonic
```

Options:
- `--host`: UnitAPI server host (default: localhost)
- `--port`: UnitAPI server port (default: 7890)
- `--debug`: Enable debug logging
- `--demo`: Demo to run (choices: dht, ultrasonic, pir, multi)
- `--dht-pin`: GPIO pin for DHT sensor (default: 4)
- `--dht-type`: DHT sensor type (choices: DHT11, DHT22) (default: DHT22)
- `--ultrasonic-trigger`: GPIO pin for ultrasonic sensor trigger (default: 23)
- `--ultrasonic-echo`: GPIO pin for ultrasonic sensor echo (default: 24)
- `--pir-pin`: GPIO pin for PIR motion sensor (default: 17)
- `--duration`: Duration of the demo in seconds (default: 30)

## Supported GPIO Operations

The GPIO examples support the following operations:

- **Set Pin Mode**: Configure a pin as input or output
- **Digital Read**: Read the state of an input pin (HIGH/LOW)
- **Digital Write**: Set the state of an output pin (HIGH/LOW)
- **PWM Control**: Generate PWM signals for dimming LEDs, controlling motors, etc.
- **Sensor Reading**: Read values from various sensors connected to GPIO pins

## GPIO Pin Numbering

These examples use the BCM (Broadcom) pin numbering scheme, not the physical pin numbers on the Raspberry Pi header. To convert between different numbering schemes, refer to a Raspberry Pi GPIO pinout diagram.

## Safety Considerations

- Be careful when connecting components to GPIO pins. Incorrect wiring can damage your Raspberry Pi.
- Always connect LEDs with appropriate resistors (typically 220-330 ohms) to prevent damage.
- For sensors that require 5V, make sure they have proper level shifting for the GPIO pins which operate at 3.3V.
- Never connect a GPIO pin directly to 5V or ground, as this can damage the pin or the entire Raspberry Pi.

## Troubleshooting

1. **Permission Issues**: If you encounter permission errors when accessing GPIO pins, try running the server with sudo:
   ```bash
   sudo python gpio_server.py
   ```

2. **Pin Already in Use**: If you get an error that a pin is already in use, make sure no other program is using that pin, or choose a different pin.

3. **Connection Issues**: Ensure the server is running and accessible from the client's network.

4. **Wiring Issues**: Double-check your wiring connections. Use a multimeter to verify connections if necessary.

## Example Use Cases

1. **Home Automation**: Control lights, fans, and other appliances remotely
2. **Environmental Monitoring**: Monitor temperature, humidity, and other environmental conditions
3. **Security Systems**: Create motion detection systems with PIR sensors
4. **Interactive Projects**: Build interactive projects with buttons, LEDs, and displays
