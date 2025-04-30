"""
Gamepad device implementation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple

from .base import InputDevice, DeviceStatus


class GamepadDevice(InputDevice):
    """
    Gamepad device implementation.
    """

    def __init__(
        self, device_id: str, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize gamepad device.

        Args:
            device_id: Unique device identifier
            name: Device name
            metadata: Additional device information
        """
        super().__init__(
            device_id=device_id, name=name, device_type="gamepad", metadata=metadata
        )
        self.logger = logging.getLogger(__name__)
        
        # Gamepad-specific attributes
        self.buttons = {
            "a": False,
            "b": False,
            "x": False,
            "y": False,
            "left_bumper": False,
            "right_bumper": False,
            "left_trigger": 0.0,  # Analog value 0.0-1.0
            "right_trigger": 0.0,  # Analog value 0.0-1.0
            "back": False,
            "start": False,
            "left_stick_button": False,
            "right_stick_button": False,
            "dpad_up": False,
            "dpad_down": False,
            "dpad_left": False,
            "dpad_right": False,
            "guide": False,  # Xbox button, PS button, etc.
        }
        
        # Analog sticks (x, y) where each axis ranges from -1.0 to 1.0
        self.left_stick = (0.0, 0.0)
        self.right_stick = (0.0, 0.0)
        
        # Vibration/rumble state
        self.vibration = {
            "left_motor": 0.0,  # 0.0-1.0
            "right_motor": 0.0,  # 0.0-1.0
        }
        
        # Controller type
        self.controller_type = metadata.get("controller_type", "xbox") if metadata else "xbox"
        
        # Battery level (0.0-1.0)
        self.battery_level = metadata.get("battery_level", 1.0) if metadata else 1.0

    async def press_button(self, button: str) -> Dict[str, Any]:
        """
        Press and release a button.

        Args:
            button: Button name

        Returns:
            Button press operation result
        """
        try:
            if button not in self.buttons:
                raise ValueError(f"Unsupported button: {button}")
                
            self.logger.info(f"Pressing button: {button}")
            
            # Press button
            await self.button_down(button)
            await asyncio.sleep(0.1)
            
            # Release button
            result = await self.button_up(button)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "action": "press",
            }
        except Exception as e:
            self.logger.error(f"Button press failed: {e}")
            return {"error": str(e)}

    async def button_down(self, button: str) -> Dict[str, Any]:
        """
        Press and hold a button.

        Args:
            button: Button name

        Returns:
            Button press operation result
        """
        try:
            if button not in self.buttons:
                raise ValueError(f"Unsupported button: {button}")
                
            self.logger.info(f"Button down: {button}")
            
            # Set button state
            if button in ["left_trigger", "right_trigger"]:
                self.buttons[button] = 1.0  # Full press for triggers
            else:
                self.buttons[button] = True
            
            # Simulate button press
            await asyncio.sleep(0.05)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "state": "down",
            }
        except Exception as e:
            self.logger.error(f"Button down failed: {e}")
            return {"error": str(e)}

    async def button_up(self, button: str) -> Dict[str, Any]:
        """
        Release a button.

        Args:
            button: Button name

        Returns:
            Button release operation result
        """
        try:
            if button not in self.buttons:
                raise ValueError(f"Unsupported button: {button}")
                
            self.logger.info(f"Button up: {button}")
            
            # Set button state
            if button in ["left_trigger", "right_trigger"]:
                self.buttons[button] = 0.0  # Release for triggers
            else:
                self.buttons[button] = False
            
            # Simulate button release
            await asyncio.sleep(0.05)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "state": "up",
            }
        except Exception as e:
            self.logger.error(f"Button up failed: {e}")
            return {"error": str(e)}

    async def set_trigger(self, trigger: str, value: float) -> Dict[str, Any]:
        """
        Set trigger value.

        Args:
            trigger: Trigger name ('left_trigger' or 'right_trigger')
            value: Trigger value (0.0-1.0)

        Returns:
            Trigger operation result
        """
        try:
            if trigger not in ["left_trigger", "right_trigger"]:
                raise ValueError(f"Unsupported trigger: {trigger}")
                
            # Clamp value between 0.0 and 1.0
            value = max(0.0, min(1.0, value))
            
            self.logger.info(f"Setting {trigger} to {value}")
            
            # Set trigger value
            self.buttons[trigger] = value
            
            # Simulate trigger movement
            await asyncio.sleep(0.05)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "trigger": trigger,
                "value": value,
            }
        except Exception as e:
            self.logger.error(f"Set trigger failed: {e}")
            return {"error": str(e)}

    async def move_stick(
        self, stick: str, x: float, y: float
    ) -> Dict[str, Any]:
        """
        Move an analog stick.

        Args:
            stick: Stick name ('left_stick' or 'right_stick')
            x: X-axis value (-1.0 to 1.0)
            y: Y-axis value (-1.0 to 1.0)

        Returns:
            Stick movement operation result
        """
        try:
            if stick not in ["left_stick", "right_stick"]:
                raise ValueError(f"Unsupported stick: {stick}")
                
            # Clamp values between -1.0 and 1.0
            x = max(-1.0, min(1.0, x))
            y = max(-1.0, min(1.0, y))
            
            self.logger.info(f"Moving {stick} to ({x}, {y})")
            
            # Set stick position
            if stick == "left_stick":
                self.left_stick = (x, y)
            else:
                self.right_stick = (x, y)
            
            # Simulate stick movement
            await asyncio.sleep(0.05)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "stick": stick,
                "position": (x, y),
            }
        except Exception as e:
            self.logger.error(f"Move stick failed: {e}")
            return {"error": str(e)}

    async def set_vibration(
        self, left_motor: float = None, right_motor: float = None
    ) -> Dict[str, Any]:
        """
        Set vibration/rumble intensity.

        Args:
            left_motor: Left motor intensity (0.0-1.0)
            right_motor: Right motor intensity (0.0-1.0)

        Returns:
            Vibration operation result
        """
        try:
            # Update left motor if provided
            if left_motor is not None:
                # Clamp value between 0.0 and 1.0
                left_motor = max(0.0, min(1.0, left_motor))
                self.vibration["left_motor"] = left_motor
            
            # Update right motor if provided
            if right_motor is not None:
                # Clamp value between 0.0 and 1.0
                right_motor = max(0.0, min(1.0, right_motor))
                self.vibration["right_motor"] = right_motor
            
            self.logger.info(
                f"Setting vibration: left={self.vibration['left_motor']}, "
                f"right={self.vibration['right_motor']}"
            )
            
            # Simulate vibration
            await asyncio.sleep(0.05)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "vibration": self.vibration.copy(),
            }
        except Exception as e:
            self.logger.error(f"Set vibration failed: {e}")
            return {"error": str(e)}

    async def reset_state(self) -> Dict[str, Any]:
        """
        Reset all buttons and sticks to their default state.

        Returns:
            Reset operation result
        """
        try:
            self.logger.info("Resetting gamepad state")
            
            # Reset buttons
            for button in self.buttons:
                if button in ["left_trigger", "right_trigger"]:
                    self.buttons[button] = 0.0
                else:
                    self.buttons[button] = False
            
            # Reset sticks
            self.left_stick = (0.0, 0.0)
            self.right_stick = (0.0, 0.0)
            
            # Reset vibration
            self.vibration["left_motor"] = 0.0
            self.vibration["right_motor"] = 0.0
            
            # Simulate reset
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "device_id": self.device_id,
                "action": "reset",
            }
        except Exception as e:
            self.logger.error(f"Reset state failed: {e}")
            return {"error": str(e)}

    async def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the gamepad.

        Returns:
            Current gamepad state
        """
        try:
            return {
                "status": "success",
                "device_id": self.device_id,
                "buttons": self.buttons.copy(),
                "left_stick": self.left_stick,
                "right_stick": self.right_stick,
                "vibration": self.vibration.copy(),
                "battery_level": self.battery_level,
            }
        except Exception as e:
            self.logger.error(f"Get state failed: {e}")
            return {"error": str(e)}

    async def connect(self) -> bool:
        """
        Connect to the gamepad device.

        Returns:
            Connection status
        """
        try:
            # Simulated connection logic
            await asyncio.sleep(0.5)
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Gamepad {self.device_id} connected")
            
            # Reset state on connect
            await self.reset_state()
            
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Gamepad connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the gamepad device.

        Returns:
            Disconnection status
        """
        try:
            # Reset state before disconnecting
            await self.reset_state()
            
            # Simulated disconnection logic
            await asyncio.sleep(0.3)
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Gamepad {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Gamepad disconnection failed: {e}")
            return False

    async def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on the gamepad device.

        Args:
            command: Command to execute
            params: Command parameters

        Returns:
            Command execution result

        Raises:
            ValueError: If command is not supported
        """
        params = params or {}
        
        try:
            if command == "press_button":
                button = params.get("button")
                if not button:
                    raise ValueError("Button parameter is required")
                return await self.press_button(button)
            elif command == "button_down":
                button = params.get("button")
                if not button:
                    raise ValueError("Button parameter is required")
                return await self.button_down(button)
            elif command == "button_up":
                button = params.get("button")
                if not button:
                    raise ValueError("Button parameter is required")
                return await self.button_up(button)
            elif command == "set_trigger":
                trigger = params.get("trigger")
                value = params.get("value", 1.0)
                if not trigger:
                    raise ValueError("Trigger parameter is required")
                return await self.set_trigger(trigger, value)
            elif command == "move_stick":
                stick = params.get("stick")
                x = params.get("x", 0.0)
                y = params.get("y", 0.0)
                if not stick:
                    raise ValueError("Stick parameter is required")
                return await self.move_stick(stick, x, y)
            elif command == "set_vibration":
                left_motor = params.get("left_motor")
                right_motor = params.get("right_motor")
                return await self.set_vibration(left_motor, right_motor)
            elif command == "reset_state":
                return await self.reset_state()
            elif command == "get_state":
                return await self.get_state()
            else:
                raise ValueError(f"Unsupported command: {command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
