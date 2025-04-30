#!/usr/bin/env python3
"""
Raspberry Pi GPIO Control Example

This script demonstrates how to control GPIO pins on a Raspberry Pi using UnitAPI.
It shows basic operations like setting pin modes, digital read/write, and PWM control.
"""

import asyncio
import argparse
import logging
import time
from typing import Dict, Any, List

from unitapi.core.client import UnitAPIClient
from unitapi.devices.gpio import GPIODevice


class RPiGPIOExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi GPIO example.

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

    async def digital_read(self, pin: int) -> Dict[str, Any]:
        """
        Read digital value from GPIO pin.

        Args:
            pin: GPIO pin number

        Returns:
            Command result with pin value
        """
        try:
            self.logger.info(f"Reading value from pin {pin}")
            
            # Execute command
            result = await self.client.execute_command(
                device_id=self.gpio_device_id,
                command='digital_read',
                params={'pin': pin}
            )
            
            if 'error' in result:
                self.logger.error(f"Digital read failed: {result['error']}")
            else:
                value = result.get('value')
                self.logger.info(f"Pin {pin} value: {value}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to read from pin: {e}")
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

    async def blink_led(self, pin: int, count: int = 5, interval: float = 0.5) -> bool:
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
            
            self.logger.info(f"Blinking LED on pin {pin} {count} times")
            
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

    async def fade_led(self, pin: int, steps: int = 20, interval: float = 0.1) -> bool:
        """
        Fade an LED connected to a GPIO pin using PWM.

        Args:
            pin: GPIO pin number
            steps: Number of fade steps
            interval: Step interval in seconds

        Returns:
            Success status
        """
        try:
            # Set pin mode to output
            await self.set_pin_mode(pin, 'output')
            
            self.logger.info(f"Fading LED on pin {pin}")
            
            # Fade up
            for i in range(steps + 1):
                duty_cycle = i / steps
                await self.pwm_write(pin, duty_cycle)
                await asyncio.sleep(interval)
                
            # Fade down
            for i in range(steps, -1, -1):
                duty_cycle = i / steps
                await self.pwm_write(pin, duty_cycle)
                await asyncio.sleep(interval)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fade LED: {e}")
            return False

    async def monitor_button(self, pin: int, duration: float = 10.0) -> bool:
        """
        Monitor a button connected to a GPIO pin.

        Args:
            pin: GPIO pin number
            duration: Monitoring duration in seconds

        Returns:
            Success status
        """
        try:
            # Set pin mode to input
            await self.set_pin_mode(pin, 'input')
            
            self.logger.info(f"Monitoring button on pin {pin} for {duration} seconds")
            
            # Record start time
            start_time = time.time()
            
            # Monitor the button
            while time.time() - start_time < duration:
                result = await self.digital_read(pin)
                
                if 'error' not in result:
                    value = result.get('value')
                    if value:
                        self.logger.info(f"Button on pin {pin} pressed!")
                
                # Wait before next read
                await asyncio.sleep(0.1)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to monitor button: {e}")
            return False


async def main():
    """
    Run the Raspberry Pi GPIO example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi GPIO Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--led-pin', type=int, default=18, help='GPIO pin for LED')
    parser.add_argument('--button-pin', type=int, default=17, help='GPIO pin for button')
    parser.add_argument('--demo', choices=['blink', 'fade', 'button', 'all'], default='all', 
                        help='Demo to run (blink, fade, button, or all)')
    
    args = parser.parse_args()
    
    example = RPiGPIOExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover GPIO device
    if not await example.discover_gpio_device():
        print("Failed to discover GPIO device. Make sure the UnitAPI server is running.")
        return
    
    # Run the selected demo
    if args.demo == 'blink' or args.demo == 'all':
        await example.blink_led(args.led_pin)
        
    if args.demo == 'fade' or args.demo == 'all':
        await example.fade_led(args.led_pin)
        
    if args.demo == 'button' or args.demo == 'all':
        await example.monitor_button(args.button_pin, duration=5.0)


if __name__ == "__main__":
    asyncio.run(main())
