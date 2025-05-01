"""
Mouse device implementation with physical mouse control using PyAutoGUI.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, Optional, Tuple

# Try to import pyautogui, but provide a mock implementation if it's not available
# This allows tests to run without requiring tkinter to be installed
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except (ImportError, ModuleNotFoundError, SystemExit):
    # Create a mock pyautogui module for testing
    # SystemExit is caught here because mouseinfo (imported by pyautogui)
    # calls sys.exit() when tkinter is not available
    PYAUTOGUI_AVAILABLE = False

    class PyAutoGUIMock:
        """Mock implementation of PyAutoGUI for testing."""

        @staticmethod
        def moveTo(x, y):
            """Mock moveTo method."""
            logging.getLogger(__name__).info(f"Mock: Moving to ({x}, {y})")

        @staticmethod
        def moveRel(dx, dy):
            """Mock moveRel method."""
            logging.getLogger(__name__).info(f"Mock: Moving by ({dx}, {dy})")

        @staticmethod
        def click(button="left"):
            """Mock click method."""
            logging.getLogger(__name__).info(f"Mock: Clicking {button} button")

        @staticmethod
        def doubleClick(button="left"):
            """Mock doubleClick method."""
            logging.getLogger(__name__).info(f"Mock: Double-clicking {button} button")

        @staticmethod
        def mouseDown(button="left"):
            """Mock mouseDown method."""
            logging.getLogger(__name__).info(f"Mock: Pressing {button} button")

        @staticmethod
        def mouseUp(button="left"):
            """Mock mouseUp method."""
            logging.getLogger(__name__).info(f"Mock: Releasing {button} button")

        @staticmethod
        def scroll(amount):
            """Mock scroll method."""
            logging.getLogger(__name__).info(f"Mock: Scrolling {amount}")

        @staticmethod
        def dragTo(x, y, button="left"):
            """Mock dragTo method."""
            logging.getLogger(__name__).info(
                f"Mock: Dragging to ({x}, {y}) with {button} button"
            )

    # Use the mock implementation
    pyautogui = PyAutoGUIMock()

from .base import InputDevice, DeviceStatus


class MouseDevice(InputDevice):
    """
    Mouse device implementation.
    """

    def __init__(
        self, device_id: str, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize mouse device.

        Args:
            device_id: Unique device identifier
            name: Device name
            metadata: Additional device information
        """
        super().__init__(
            device_id=device_id, name=name, device_type="mouse", metadata=metadata
        )
        self.logger = logging.getLogger(__name__)

        # Mouse-specific attributes
        self._position = (0, 0)  # Initialize position to (0, 0)
        self.buttons_state = {
            "left": False,
            "right": False,
            "middle": False,
        }

    @property
    def position(self) -> Tuple[int, int]:
        """
        Get the current mouse position.

        Returns:
            Current mouse position as (x, y) tuple
        """
        return self._position

    @position.setter
    def position(self, pos: Tuple[int, int]) -> None:
        """
        Set the internal position tracking (not the actual mouse position).

        Args:
            pos: Position as (x, y) tuple
        """
        self._position = pos

    async def move_to(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse cursor to absolute position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Movement operation result
        """
        try:
            self.logger.info(f"Moving mouse to position ({x}, {y})")

            # Move the physical mouse using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.moveTo(x, y)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse movement to ({x}, {y})"
                )

            # Update internal position tracking
            self._position = (x, y)

            return {
                "status": "success",
                "device_id": self.device_id,
                "position": self.position,
            }
        except Exception as e:
            self.logger.error(f"Mouse movement failed: {e}")
            return {"error": str(e)}

    async def move_relative(self, dx: int, dy: int) -> Dict[str, Any]:
        """
        Move mouse cursor by a relative amount.

        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate

        Returns:
            Movement operation result
        """
        try:
            x, y = self.position
            new_x, new_y = x + dx, y + dy
            self.logger.info(f"Moving mouse by ({dx}, {dy}) to ({new_x}, {new_y})")

            # Move the physical mouse using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.moveRel(dx, dy)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating relative mouse movement by ({dx}, {dy})"
                )

            # Update internal position tracking
            self._position = (new_x, new_y)

            return {
                "status": "success",
                "device_id": self.device_id,
                "position": self.position,
            }
        except Exception as e:
            self.logger.error(f"Relative mouse movement failed: {e}")
            return {"error": str(e)}

    async def click(self, button: str = "left") -> Dict[str, Any]:
        """
        Perform a mouse click.

        Args:
            button: Mouse button to click ('left', 'right', 'middle')

        Returns:
            Click operation result
        """
        try:
            if button not in self.buttons_state:
                raise ValueError(f"Unsupported mouse button: {button}")

            self.logger.info(f"Clicking {button} mouse button at {self.position}")

            # Use button_down and button_up methods
            down_result = await self.button_down(button)
            if "error" in down_result:
                return down_result

            up_result = await self.button_up(button)
            if "error" in up_result:
                return up_result

            # Also perform the physical click using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.click(button=button)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse click with {button} button"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "position": self.position,
            }
        except Exception as e:
            self.logger.error(f"Mouse click failed: {e}")
            return {"error": str(e)}

    async def double_click(self, button: str = "left") -> Dict[str, Any]:
        """
        Perform a mouse double-click.

        Args:
            button: Mouse button to double-click ('left', 'right', 'middle')

        Returns:
            Double-click operation result
        """
        try:
            if button not in self.buttons_state:
                raise ValueError(f"Unsupported mouse button: {button}")

            self.logger.info(
                f"Double-clicking {button} mouse button at {self.position}"
            )

            # Double-click the physical mouse using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.doubleClick(button=button)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse double-click with {button} button"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "position": self.position,
            }
        except Exception as e:
            self.logger.error(f"Mouse double-click failed: {e}")
            return {"error": str(e)}

    async def button_down(self, button: str = "left") -> Dict[str, Any]:
        """
        Press and hold a mouse button.

        Args:
            button: Mouse button to press ('left', 'right', 'middle')

        Returns:
            Button press operation result
        """
        try:
            if button not in self.buttons_state:
                raise ValueError(f"Unsupported mouse button: {button}")

            self.logger.info(f"Pressing {button} mouse button at {self.position}")

            # Press the physical mouse button using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.mouseDown(button=button)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse button down with {button} button"
                )

            # Update button state
            self.buttons_state[button] = True

            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "position": self.position,
                "state": "down",
            }
        except Exception as e:
            self.logger.error(f"Mouse button down failed: {e}")
            return {"error": str(e)}

    async def button_up(self, button: str = "left") -> Dict[str, Any]:
        """
        Release a mouse button.

        Args:
            button: Mouse button to release ('left', 'right', 'middle')

        Returns:
            Button release operation result
        """
        try:
            if button not in self.buttons_state:
                raise ValueError(f"Unsupported mouse button: {button}")

            self.logger.info(f"Releasing {button} mouse button at {self.position}")

            # Release the physical mouse button using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.mouseUp(button=button)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse button up with {button} button"
                )

            # Update button state
            self.buttons_state[button] = False

            return {
                "status": "success",
                "device_id": self.device_id,
                "button": button,
                "position": self.position,
                "state": "up",
            }
        except Exception as e:
            self.logger.error(f"Mouse button up failed: {e}")
            return {"error": str(e)}

    async def scroll(self, amount: int) -> Dict[str, Any]:
        """
        Scroll the mouse wheel.

        Args:
            amount: Scroll amount (positive for up, negative for down)

        Returns:
            Scroll operation result
        """
        try:
            direction = "up" if amount > 0 else "down"
            self.logger.info(
                f"Scrolling {direction} by {abs(amount)} at {self.position}"
            )

            # Scroll the physical mouse wheel using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.scroll(amount)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse scroll by {amount}"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "scroll_amount": amount,
                "position": self.position,
            }
        except Exception as e:
            self.logger.error(f"Mouse scroll failed: {e}")
            return {"error": str(e)}

    async def drag(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        """
        Perform a drag operation from current position to target position.

        Args:
            x: Target X coordinate
            y: Target Y coordinate
            button: Mouse button to use for dragging ('left', 'right', 'middle')

        Returns:
            Drag operation result
        """
        try:
            start_x, start_y = self.position
            self.logger.info(
                f"Dragging from ({start_x}, {start_y}) to ({x}, {y}) "
                f"with {button} button"
            )

            # Use button_down, move_to, and button_up methods
            down_result = await self.button_down(button)
            if "error" in down_result:
                return down_result

            move_result = await self.move_to(x, y)
            if "error" in move_result:
                return move_result

            up_result = await self.button_up(button)
            if "error" in up_result:
                return up_result

            # Also perform the physical drag using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.dragTo(x, y, button=button)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating mouse drag to ({x}, {y}) with {button} button"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "start_position": (start_x, start_y),
                "end_position": (x, y),
                "button": button,
            }
        except Exception as e:
            self.logger.error(f"Mouse drag failed: {e}")
            return {"error": str(e)}

    async def connect(self) -> bool:
        """
        Connect to the mouse device.

        Returns:
            Connection status
        """
        try:
            # Simulated connection logic
            await asyncio.sleep(0.5)
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Mouse {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Mouse connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the mouse device.

        Returns:
            Disconnection status
        """
        try:
            # Simulated disconnection logic
            await asyncio.sleep(0.3)
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Mouse {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Mouse disconnection failed: {e}")
            return False

    async def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on the mouse device.

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
            if command == "move_to":
                x = params.get("x", 0)
                y = params.get("y", 0)
                return await self.move_to(x, y)
            elif command == "move_relative":
                dx = params.get("dx", 0)
                dy = params.get("dy", 0)
                return await self.move_relative(dx, dy)
            elif command == "click":
                button = params.get("button", "left")
                return await self.click(button)
            elif command == "double_click":
                button = params.get("button", "left")
                return await self.double_click(button)
            elif command == "button_down":
                button = params.get("button", "left")
                return await self.button_down(button)
            elif command == "button_up":
                button = params.get("button", "left")
                return await self.button_up(button)
            elif command == "scroll":
                amount = params.get("amount", 0)
                return await self.scroll(amount)
            elif command == "drag":
                x = params.get("x", 0)
                y = params.get("y", 0)
                button = params.get("button", "left")
                return await self.drag(x, y, button)
            else:
                raise ValueError(f"Unsupported command: {command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
