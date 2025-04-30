#!/usr/bin/env python3
"""
Raspberry Pi LED Control Example

This script demonstrates how to control LEDs using Raspberry Pi GPIO pins with UnitAPI.
It includes examples for blinking, fading, patterns, and RGB LED control.
"""

import asyncio
import argparse
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from unitapi.core.client import UnitAPIClient
from unitapi.devices.gpio import GPIODevice


class RPiLEDExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi LED control example.

        Args:
            server_host: UnitAPI server host
            server_port: UnitAPI server port
            debug: Enable debug logging
        """
        # Configure logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # UnitAPI client
        self.client = UnitAPIClient(
            server_host=server_host,
            server_port=server_port
        )
        
        # GPIO device
        self.gpio_device = None
        self.gpio_device_id = None

    async def discover_gpio_device(self) -> bool:
        """
        Discover GPIO device on the Raspberry Pi.

        Returns:
            Success status
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for GPIO devices
            gpio_devices = [
                device for device in devices
                if device.get('type') == 'gpio'
            ]
            
            if gpio_devices:
                self.logger.info(f"Found {len(gpio_devices)} GPIO device(s)")
                for i, device in enumerate(gpio_devices):
                    self.logger.info(f"GPIO Device {i+1}: {device.get('name')} (ID: {device.get('device_id')})")
                
                # Use the first GPIO device
                self.gpio_device_id = gpio_devices[0].get('device_id')
                return True
            else:
                self.logger.warning("No GPIO devices found. Creating a local GPIO device.")
                
                # Create a local GPIO device for demonstration
                self.gpio_device = GPIODevice(
                    device_id="gpio_rpi",
                    name="Raspberry Pi GPIO",
                    metadata={"platform": "raspberry_pi"}
                )
                
                # Connect the device
                await self.gpio_device.connect()
                
                self.gpio_device_id = self.gpio_device.device_id
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to discover GPIO device: {e}")
            return False

    async def set_pin_mode(self, pin: int, mode: str) -> Dict[str, Any]:
        """
        Set GPIO pin mode.

        Args:
            pin: GPIO pin number
            mode: Pin mode ('input' or 'output')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Setting pin {pin} mode to {mode}")
            
            # Execute command
            result = await self.client.execute_command(
                device_id=self.gpio_device_id,
                command='set_pin_mode',
                params={'pin': pin, 'mode': mode}
            )
            
            if 'error' in result:
                self.logger.error(f"Set pin mode failed: {result['error']}")
            else:
                self.logger.info(f"Pin {pin} mode set to {mode}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to set pin mode: {e}")
            return {'error': str(e)}

    async def digital_write(self, pin: int, value: bool) -> Dict[str, Any]:
        """
        Write digital value to GPIO pin.

        Args:
            pin: GPIO pin number
            value: Digital value to write (True for HIGH, False for LOW)

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Writing value {value} to pin {pin}")
            
            # Execute command
            result = await self.client.execute_command(
                device_id=self.gpio_device_id,
                command='digital_write',
                params={'pin': pin, 'value': value}
            )
            
            if 'error' in result:
                self.logger.error(f"Digital write failed: {result['error']}")
            else:
                self.logger.info(f"Value {value} written to pin {pin}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to write to pin: {e}")
            return {'error': str(e)}

    async def pwm_write(self, pin: int, duty_cycle: float) -> Dict[str, Any]:
        """
        Write PWM value to GPIO pin.

        Args:
            pin: GPIO pin number
            duty_cycle: PWM duty cycle (0.0 to 1.0)

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Writing PWM duty cycle {duty_cycle} to pin {pin}")
            
            # Execute command
            result = await self.client.execute_command(
                device_id=self.gpio_device_id,
                command='pwm_write',
                params={'pin': pin, 'duty_cycle': duty_cycle}
            )
            
            if 'error' in result:
                self.logger.error(f"PWM write failed: {result['error']}")
            else:
                self.logger.info(f"PWM duty cycle {duty_cycle} written to pin {pin}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to write PWM to pin: {e}")
            return {'error': str(e)}

    async def blink_led(
            self,
            pin: int,
            count: int = 10,
            interval: float = 0.5
    ) -> bool:
        """
        Blink an LED connected to a GPIO pin.

        Args:
            pin: GPIO pin number
            count: Number of blinks
            interval: Blink interval in seconds

        Returns:
            Success status
        """
        try:
            # Set pin mode to output
            await self.set_pin_mode(pin, 'output')
            
            self.logger.info(f"Blinking LED on pin {pin} {count} times with {interval}s interval")
            
            # Blink the LED
            for i in range(count):
                # Turn on
                await self.digital_write(pin, True)
                await asyncio.sleep(interval)
                
                # Turn off
                await self.digital_write(pin, False)
                await asyncio.sleep(interval)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to blink LED: {e}")
            return False

    async def fade_led(
            self,
            pin: int,
            steps: int = 100,
            duration: float = 5.0,
            repeat: int = 1
    ) -> bool:
        """
        Fade an LED connected to a GPIO pin using PWM.

        Args:
            pin: GPIO pin number
            steps: Number of fade steps
            duration: Total fade cycle duration in seconds
            repeat: Number of fade cycles to repeat

        Returns:
            Success status
        """
        try:
            # Set pin mode to output
            await self.set_pin_mode(pin, 'output')
            
            self.logger.info(f"Fading LED on pin {pin} over {duration}s ({repeat} times)")
            
            # Calculate step interval
            step_interval = duration / (steps * 2)  # *2 for fade up and down
            
            for r in range(repeat):
                # Fade up
                for i in range(steps + 1):
                    duty_cycle = i / steps
                    await self.pwm_write(pin, duty_cycle)
                    await asyncio.sleep(step_interval)
                    
                # Fade down
                for i in range(steps, -1, -1):
                    duty_cycle = i / steps
                    await self.pwm_write(pin, duty_cycle)
                    await asyncio.sleep(step_interval)
                
            # Ensure LED is off at the end
            await self.digital_write(pin, False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fade LED: {e}")
            return False

    async def pulse_led(
            self,
            pin: int,
            count: int = 5,
            pulse_width: float = 0.5
    ) -> bool:
        """
        Pulse an LED with a smoother transition than blinking.

        Args:
            pin: GPIO pin number
            count: Number of pulses
            pulse_width: Width of each pulse in seconds

        Returns:
            Success status
        """
        try:
            # Set pin mode to output
            await self.set_pin_mode(pin, 'output')
            
            self.logger.info(f"Pulsing LED on pin {pin} {count} times")
            
            # Number of steps for smooth transition
            steps = 20
            
            for c in range(count):
                # Pulse up
                for i in range(steps + 1):
                    duty_cycle = i / steps
                    await self.pwm_write(pin, duty_cycle)
                    await asyncio.sleep(pulse_width / (steps * 2))
                
                # Hold at peak
                await asyncio.sleep(pulse_width / 2)
                
                # Pulse down
                for i in range(steps, -1, -1):
                    duty_cycle = i / steps
                    await self.pwm_write(pin, duty_cycle)
                    await asyncio.sleep(pulse_width / (steps * 2))
                
                # Pause between pulses
                await asyncio.sleep(pulse_width)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pulse LED: {e}")
            return False

    async def led_pattern(
            self,
            pins: List[int],
            pattern: str = 'chase',
            cycles: int = 3,
            speed: float = 0.2
    ) -> bool:
        """
        Run a pattern on multiple LEDs.

        Args:
            pins: List of GPIO pin numbers
            pattern: Pattern type ('chase', 'alternate', 'flash', 'random')
            cycles: Number of pattern cycles
            speed: Pattern speed (lower is faster)

        Returns:
            Success status
        """
        try:
            # Set all pins to output mode
            for pin in pins:
                await self.set_pin_mode(pin, 'output')
                # Ensure all LEDs start off
                await self.digital_write(pin, False)
            
            self.logger.info(f"Running '{pattern}' pattern on pins {pins} for {cycles} cycles")
            
            # Run the selected pattern
            if pattern == 'chase':
                # Chase pattern (one LED at a time in sequence)
                for c in range(cycles):
                    for i, pin in enumerate(pins):
                        # Turn on current LED
                        await self.digital_write(pin, True)
                        await asyncio.sleep(speed)
                        
                        # Turn off current LED
                        await self.digital_write(pin, False)
            
            elif pattern == 'alternate':
                # Alternate pattern (alternate between even and odd LEDs)
                for c in range(cycles):
                    # Turn on even pins, off odd pins
                    for i, pin in enumerate(pins):
                        await self.digital_write(pin, i % 2 == 0)
                    await asyncio.sleep(speed)
                    
                    # Turn on odd pins, off even pins
                    for i, pin in enumerate(pins):
                        await self.digital_write(pin, i % 2 != 0)
                    await asyncio.sleep(speed)
            
            elif pattern == 'flash':
                # Flash pattern (all LEDs on/off together)
                for c in range(cycles):
                    # All on
                    for pin in pins:
                        await self.digital_write(pin, True)
                    await asyncio.sleep(speed)
                    
                    # All off
                    for pin in pins:
                        await self.digital_write(pin, False)
                    await asyncio.sleep(speed)
            
            elif pattern == 'random':
                # Random pattern
                import random
                
                for c in range(cycles * 2):  # *2 for more variation
                    # Set random state for each LED
                    for pin in pins:
                        state = random.choice([True, False])
                        await self.digital_write(pin, state)
                    await asyncio.sleep(speed)
            
            else:
                self.logger.error(f"Unknown pattern: {pattern}")
                return False
            
            # Ensure all LEDs are off at the end
            for pin in pins:
                await self.digital_write(pin, False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to run LED pattern: {e}")
            
            # Try to turn off all LEDs in case of error
            try:
                for pin in pins:
                    await self.digital_write(pin, False)
            except:
                pass
                
            return False

    async def control_rgb_led(
            self,
            red_pin: int,
            green_pin: int,
            blue_pin: int,
            mode: str = 'cycle',
            duration: float = 10.0
    ) -> bool:
        """
        Control an RGB LED connected to three GPIO pins.

        Args:
            red_pin: GPIO pin for red channel
            green_pin: GPIO pin for green channel
            blue_pin: GPIO pin for blue channel
            mode: Control mode ('cycle', 'random', 'fade')
            duration: Duration of the demonstration in seconds

        Returns:
            Success status
        """
        try:
            # Set all pins to output mode
            for pin in [red_pin, green_pin, blue_pin]:
                await self.set_pin_mode(pin, 'output')
                # Ensure all channels start off
                await self.digital_write(pin, False)
            
            self.logger.info(f"Controlling RGB LED (R:{red_pin}, G:{green_pin}, B:{blue_pin}) in '{mode}' mode")
            
            # Record start time
            start_time = time.time()
            
            # Run the selected mode
            if mode == 'cycle':
                # Cycle through primary and secondary colors
                colors = [
                    (1, 0, 0),  # Red
                    (1, 1, 0),  # Yellow
                    (0, 1, 0),  # Green
                    (0, 1, 1),  # Cyan
                    (0, 0, 1),  # Blue
                    (1, 0, 1),  # Magenta
                ]
                
                # Calculate time per color
                color_time = duration / len(colors)
                
                # Cycle through colors
                while time.time() - start_time < duration:
                    elapsed = time.time() - start_time
                    color_index = int(elapsed / color_time) % len(colors)
                    
                    # Set current color
                    r, g, b = colors[color_index]
                    await self.pwm_write(red_pin, r)
                    await self.pwm_write(green_pin, g)
                    await self.pwm_write(blue_pin, b)
                    
                    # Small delay to prevent excessive updates
                    await asyncio.sleep(0.1)
            
            elif mode == 'random':
                # Random color changes
                import random
                
                # Calculate time per color change
                change_interval = 1.0  # 1 second per color
                last_change = start_time
                
                # Generate random colors
                while time.time() - start_time < duration:
                    current_time = time.time()
                    
                    # Time for a new color?
                    if current_time - last_change >= change_interval:
                        # Generate random RGB values
                        r = random.random()
                        g = random.random()
                        b = random.random()
                        
                        # Set the color
                        await self.pwm_write(red_pin, r)
                        await self.pwm_write(green_pin, g)
                        await self.pwm_write(blue_pin, b)
                        
                        last_change = current_time
                    
                    # Small delay to prevent excessive updates
                    await asyncio.sleep(0.1)
            
            elif mode == 'fade':
                # Smooth fading between colors
                import math
                
                # Continuous color wheel
                while time.time() - start_time < duration:
                    elapsed = time.time() - start_time
                    
                    # Use sine waves with phase shifts for smooth transitions
                    # Phase shift each color by 120 degrees (2π/3 radians)
                    phase_shift = 2 * math.pi / 3
                    
                    # Calculate color values (0.0 to 1.0)
                    r = (math.sin(elapsed + 0 * phase_shift) + 1) / 2
                    g = (math.sin(elapsed + 1 * phase_shift) + 1) / 2
                    b = (math.sin(elapsed + 2 * phase_shift) + 1) / 2
                    
                    # Set the color
                    await self.pwm_write(red_pin, r)
                    await self.pwm_write(green_pin, g)
                    await self.pwm_write(blue_pin, b)
                    
                    # Small delay to prevent excessive updates
                    await asyncio.sleep(0.05)
            
            else:
                self.logger.error(f"Unknown RGB mode: {mode}")
                return False
            
            # Ensure all channels are off at the end
            for pin in [red_pin, green_pin, blue_pin]:
                await self.digital_write(pin, False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to control RGB LED: {e}")
            
            # Try to turn off all channels in case of error
            try:
                for pin in [red_pin, green_pin, blue_pin]:
                    await self.digital_write(pin, False)
            except:
                pass
                
            return False


async def main():
    """
    Run the Raspberry Pi LED control example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi LED Control Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--demo', choices=['blink', 'fade', 'pulse', 'pattern', 'rgb', 'all'], 
                        default='all', help='Demo to run')
    parser.add_argument('--led-pin', type=int, default=18, help='GPIO pin for single LED')
    parser.add_argument('--led-pins', type=str, default='18,23,24,25', 
                        help='Comma-separated GPIO pins for multiple LEDs')
    parser.add_argument('--red-pin', type=int, default=17, help='GPIO pin for RGB red channel')
    parser.add_argument('--green-pin', type=int, default=27, help='GPIO pin for RGB green channel')
    parser.add_argument('--blue-pin', type=int, default=22, help='GPIO pin for RGB blue channel')
    parser.add_argument('--pattern', choices=['chase', 'alternate', 'flash', 'random'], 
                        default='chase', help='LED pattern type')
    parser.add_argument('--rgb-mode', choices=['cycle', 'random', 'fade'], 
                        default='fade', help='RGB LED control mode')
    parser.add_argument('--duration', type=float, default=5.0, help='Demo duration in seconds')
    
    args = parser.parse_args()
    
    example = RPiLEDExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover GPIO device
    if not await example.discover_gpio_device():
        print("Failed to discover GPIO device. Make sure the UnitAPI server is running.")
        return
    
    # Parse LED pins for pattern demo
    led_pins = [int(pin.strip()) for pin in args.led_pins.split(',')]
    
    # Run the selected demo
    if args.demo == 'blink' or args.demo == 'all':
        await example.blink_led(args.led_pin, count=5, interval=0.5)
        
    if args.demo == 'fade' or args.demo == 'all':
        await example.fade_led(args.led_pin, duration=3.0, repeat=2)
        
    if args.demo == 'pulse' or args.demo == 'all':
        await example.pulse_led(args.led_pin, count=3, pulse_width=0.8)
        
    if args.demo == 'pattern' or args.demo == 'all':
        await example.led_pattern(led_pins, pattern=args.pattern, cycles=2)
        
    if args.demo == 'rgb' or args.demo == 'all':
        await example.control_rgb_led(
            args.red_pin, args.green_pin, args.blue_pin,
            mode=args.rgb_mode, duration=args.duration
        )


if __name__ == "__main__":
    asyncio.run(main())
