#!/usr/bin/env python3
"""
Raspberry Pi Sensors Example

This script demonstrates how to use various sensors with Raspberry Pi GPIO pins using UnitAPI.
It includes examples for common sensors like DHT11/DHT22 (temperature/humidity),
HC-SR04 (ultrasonic distance), and PIR motion sensors.
"""

import asyncio
import argparse
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple

from unitapi.core.client import UnitAPIClient
from unitapi.devices.gpio import GPIODevice


class RPiSensorsExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Sensors example.

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

    async def read_dht_sensor(
            self,
            data_pin: int,
            sensor_type: str = 'DHT22',
            retries: int = 3
    ) -> Dict[str, Any]:
        """
        Read temperature and humidity from a DHT11/DHT22 sensor.

        Args:
            data_pin: GPIO pin connected to the DHT sensor data pin
            sensor_type: Sensor type ('DHT11' or 'DHT22')
            retries: Number of retry attempts

        Returns:
            Sensor reading result with temperature and humidity
        """
        try:
            self.logger.info(f"Reading {sensor_type} sensor on pin {data_pin}")
            
            # In a real implementation, we would use the Adafruit_DHT library
            # Here we simulate the sensor reading
            
            # Set pin mode to input
            await self.set_pin_mode(data_pin, 'input')
            
            # Simulate sensor reading (random values for demonstration)
            import random
            
            # Simulate occasional read failures
            if random.random() < 0.2 and retries <= 0:
                self.logger.warning(f"Failed to read {sensor_type} sensor")
                return {'error': 'Sensor read failed', 'status': 'error'}
            
            # Generate simulated values based on sensor type
            if sensor_type == 'DHT11':
                # DHT11 has lower precision
                temperature = round(random.uniform(0, 50), 1)
                humidity = round(random.uniform(20, 90), 1)
            else:  # DHT22
                # DHT22 has higher precision
                temperature = round(random.uniform(-40, 80), 2)
                humidity = round(random.uniform(0, 100), 2)
            
            self.logger.info(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            
            return {
                'temperature': temperature,
                'humidity': humidity,
                'sensor_type': sensor_type,
                'pin': data_pin,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to read DHT sensor: {e}")
            
            # Retry if attempts remain
            if retries > 0:
                self.logger.info(f"Retrying DHT sensor read ({retries} attempts left)")
                await asyncio.sleep(2)  # Wait before retry
                return await self.read_dht_sensor(data_pin, sensor_type, retries - 1)
                
            return {'error': str(e), 'status': 'error'}

    async def read_ultrasonic_sensor(
            self,
            trigger_pin: int,
            echo_pin: int,
            timeout: float = 1.0,
            retries: int = 3
    ) -> Dict[str, Any]:
        """
        Read distance from an HC-SR04 ultrasonic sensor.

        Args:
            trigger_pin: GPIO pin connected to the trigger pin
            echo_pin: GPIO pin connected to the echo pin
            timeout: Measurement timeout in seconds
            retries: Number of retry attempts

        Returns:
            Sensor reading result with distance in centimeters
        """
        try:
            self.logger.info(f"Reading ultrasonic sensor (trigger: {trigger_pin}, echo: {echo_pin})")
            
            # Set pin modes
            await self.set_pin_mode(trigger_pin, 'output')
            await self.set_pin_mode(echo_pin, 'input')
            
            # Ensure trigger pin is low
            await self.digital_write(trigger_pin, False)
            await asyncio.sleep(0.5)  # Wait for sensor to settle
            
            # Send 10us pulse to trigger
            await self.digital_write(trigger_pin, True)
            await asyncio.sleep(0.00001)  # 10 microseconds
            await self.digital_write(trigger_pin, False)
            
            # In a real implementation, we would measure the time between
            # echo pin going high and then low again
            # Here we simulate the sensor reading
            
            # Simulate sensor reading (random distance for demonstration)
            import random
            
            # Simulate occasional read failures
            if random.random() < 0.2 and retries <= 0:
                self.logger.warning("Failed to read ultrasonic sensor")
                return {'error': 'Sensor read failed', 'status': 'error'}
            
            # Generate simulated distance (2cm to 400cm, typical HC-SR04 range)
            distance = round(random.uniform(2, 400), 1)
            
            self.logger.info(f"Distance: {distance} cm")
            
            return {
                'distance': distance,
                'unit': 'cm',
                'trigger_pin': trigger_pin,
                'echo_pin': echo_pin,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to read ultrasonic sensor: {e}")
            
            # Retry if attempts remain
            if retries > 0:
                self.logger.info(f"Retrying ultrasonic sensor read ({retries} attempts left)")
                await asyncio.sleep(0.5)  # Wait before retry
                return await self.read_ultrasonic_sensor(trigger_pin, echo_pin, timeout, retries - 1)
                
            return {'error': str(e), 'status': 'error'}

    async def monitor_pir_sensor(
            self,
            pir_pin: int,
            duration: float = 30.0,
            callback = None
    ) -> Dict[str, Any]:
        """
        Monitor a PIR motion sensor.

        Args:
            pir_pin: GPIO pin connected to the PIR sensor output
            duration: Monitoring duration in seconds
            callback: Optional callback function to call when motion is detected

        Returns:
            Monitoring result with motion events
        """
        try:
            self.logger.info(f"Monitoring PIR motion sensor on pin {pir_pin} for {duration} seconds")
            
            # Set pin mode to input
            await self.set_pin_mode(pir_pin, 'input')
            
            # Record start time
            start_time = time.time()
            
            # Track motion events
            motion_events = []
            last_state = False
            
            # Monitor the PIR sensor
            while time.time() - start_time < duration:
                # Read sensor value
                result = await self.digital_read(pir_pin)
                
                if 'error' not in result:
                    current_state = result.get('value', False)
                    
                    # Detect rising edge (motion detected)
                    if current_state and not last_state:
                        event_time = time.time() - start_time
                        self.logger.info(f"Motion detected at {event_time:.2f}s")
                        
                        # Record event
                        event = {
                            'time': event_time,
                            'timestamp': time.time(),
                            'type': 'motion_detected'
                        }
                        motion_events.append(event)
                        
                        # Call callback if provided
                        if callback:
                            callback(event)
                    
                    last_state = current_state
                
                # Wait before next read
                await asyncio.sleep(0.1)
            
            self.logger.info(f"PIR monitoring completed. Detected {len(motion_events)} motion events.")
            
            return {
                'events': motion_events,
                'duration': duration,
                'pin': pir_pin,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor PIR sensor: {e}")
            return {'error': str(e), 'status': 'error'}

    async def monitor_multiple_sensors(
            self,
            dht_pin: Optional[int] = None,
            ultrasonic_trigger_pin: Optional[int] = None,
            ultrasonic_echo_pin: Optional[int] = None,
            pir_pin: Optional[int] = None,
            duration: float = 60.0,
            interval: float = 5.0,
            output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Monitor multiple sensors simultaneously.

        Args:
            dht_pin: GPIO pin for DHT sensor (None to skip)
            ultrasonic_trigger_pin: GPIO pin for ultrasonic trigger (None to skip)
            ultrasonic_echo_pin: GPIO pin for ultrasonic echo (None to skip)
            pir_pin: GPIO pin for PIR sensor (None to skip)
            duration: Total monitoring duration in seconds
            interval: Sensor reading interval in seconds
            output_file: Optional file to save readings

        Returns:
            Monitoring results from all sensors
        """
        try:
            self.logger.info(f"Starting multi-sensor monitoring for {duration} seconds")
            
            # Prepare sensors
            use_dht = dht_pin is not None
            use_ultrasonic = ultrasonic_trigger_pin is not None and ultrasonic_echo_pin is not None
            use_pir = pir_pin is not None
            
            if use_dht:
                self.logger.info(f"DHT sensor enabled on pin {dht_pin}")
                
            if use_ultrasonic:
                self.logger.info(f"Ultrasonic sensor enabled (trigger: {ultrasonic_trigger_pin}, echo: {ultrasonic_echo_pin})")
                
            if use_pir:
                self.logger.info(f"PIR motion sensor enabled on pin {pir_pin}")
                await self.set_pin_mode(pir_pin, 'input')
            
            # Record start time
            start_time = time.time()
            
            # Store all readings
            all_readings = []
            
            # Monitor loop
            while time.time() - start_time < duration:
                # Current timestamp
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Create reading entry
                reading = {
                    'timestamp': current_time,
                    'elapsed_seconds': elapsed
                }
                
                # Read DHT sensor
                if use_dht:
                    dht_result = await self.read_dht_sensor(dht_pin)
                    if 'error' not in dht_result:
                        reading['temperature'] = dht_result.get('temperature')
                        reading['humidity'] = dht_result.get('humidity')
                
                # Read ultrasonic sensor
                if use_ultrasonic:
                    ultrasonic_result = await self.read_ultrasonic_sensor(
                        ultrasonic_trigger_pin, ultrasonic_echo_pin
                    )
                    if 'error' not in ultrasonic_result:
                        reading['distance'] = ultrasonic_result.get('distance')
                
                # Read PIR sensor
                if use_pir:
                    pir_result = await self.digital_read(pir_pin)
                    if 'error' not in pir_result:
                        reading['motion'] = pir_result.get('value', False)
                
                # Log the reading
                self.logger.info(f"Sensor reading at {elapsed:.1f}s: {reading}")
                
                # Add to readings list
                all_readings.append(reading)
                
                # Save to file if specified
                if output_file:
                    try:
                        with open(output_file, 'w') as f:
                            json.dump(all_readings, f, indent=2)
                    except Exception as e:
                        self.logger.error(f"Failed to write to output file: {e}")
                
                # Wait for next interval (unless we've exceeded duration)
                next_reading_time = start_time + (len(all_readings) * interval)
                wait_time = max(0, next_reading_time - time.time())
                
                if wait_time > 0 and (time.time() + wait_time - start_time) < duration:
                    await asyncio.sleep(wait_time)
            
            self.logger.info(f"Multi-sensor monitoring completed. Collected {len(all_readings)} readings.")
            
            # Final save to file
            if output_file:
                try:
                    with open(output_file, 'w') as f:
                        json.dump(all_readings, f, indent=2)
                    self.logger.info(f"Sensor readings saved to {output_file}")
                except Exception as e:
                    self.logger.error(f"Failed to write to output file: {e}")
            
            return {
                'readings': all_readings,
                'duration': duration,
                'interval': interval,
                'sensors': {
                    'dht': use_dht,
                    'ultrasonic': use_ultrasonic,
                    'pir': use_pir
                },
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor multiple sensors: {e}")
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi Sensors example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Sensors Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--output', help='Output file to save readings (JSON format)')
    parser.add_argument('--demo', choices=['dht', 'ultrasonic', 'pir', 'multi'], 
                        default='multi', help='Demo to run')
    parser.add_argument('--dht-pin', type=int, default=4, help='GPIO pin for DHT sensor data')
    parser.add_argument('--dht-type', choices=['DHT11', 'DHT22'], default='DHT22', 
                        help='DHT sensor type')
    parser.add_argument('--trigger-pin', type=int, default=23, help='GPIO pin for ultrasonic trigger')
    parser.add_argument('--echo-pin', type=int, default=24, help='GPIO pin for ultrasonic echo')
    parser.add_argument('--pir-pin', type=int, default=17, help='GPIO pin for PIR motion sensor')
    parser.add_argument('--duration', type=float, default=30.0, help='Monitoring duration in seconds')
    parser.add_argument('--interval', type=float, default=2.0, help='Reading interval in seconds')
    
    args = parser.parse_args()
    
    example = RPiSensorsExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover GPIO device
    if not await example.discover_gpio_device():
        print("Failed to discover GPIO device. Make sure the UnitAPI server is running.")
        return
    
    # Run the selected demo
    if args.demo == 'dht':
        result = await example.read_dht_sensor(args.dht_pin, args.dht_type)
        print(f"DHT Sensor Reading: {result}")
        
    elif args.demo == 'ultrasonic':
        result = await example.read_ultrasonic_sensor(args.trigger_pin, args.echo_pin)
        print(f"Ultrasonic Sensor Reading: {result}")
        
    elif args.demo == 'pir':
        result = await example.monitor_pir_sensor(args.pir_pin, args.duration)
        print(f"PIR Sensor Monitoring: {len(result.get('events', []))} motion events detected")
        
    elif args.demo == 'multi':
        result = await example.monitor_multiple_sensors(
            dht_pin=args.dht_pin,
            ultrasonic_trigger_pin=args.trigger_pin,
            ultrasonic_echo_pin=args.echo_pin,
            pir_pin=args.pir_pin,
            duration=args.duration,
            interval=args.interval,
            output_file=args.output
        )
        print(f"Multi-sensor Monitoring: {len(result.get('readings', []))} readings collected")


if __name__ == "__main__":
    asyncio.run(main())
