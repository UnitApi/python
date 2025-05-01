"""
Keyboard device implementation with physical keyboard control using PyAutoGUI.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Set

# Check if we should skip tkinter-dependent functionality
SKIP_TKINTER = os.environ.get("UNITAPI_SKIP_TKINTER_TESTS", "0") == "1"

# Try to import pyautogui, but provide a mock implementation if it's not available
# This allows tests to run without requiring tkinter to be installed
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except (ImportError, ModuleNotFoundError, SystemExit) as e:
    # Create a mock pyautogui module for testing
    # SystemExit is caught here because mouseinfo (imported by pyautogui)
    # calls sys.exit() when tkinter is not available
    PYAUTOGUI_AVAILABLE = False

    if not SKIP_TKINTER:
        logging.getLogger(__name__).warning(f"PyAutoGUI import failed: {e}")

    class MockPyAutoGUI:
        """Mock implementation of PyAutoGUI for testing."""

        @staticmethod
        def keyDown(key):
            """Mock keyDown method."""
            logging.getLogger(__name__).info(f"Mock: Pressing key {key}")

        @staticmethod
        def keyUp(key):
            """Mock keyUp method."""
            logging.getLogger(__name__).info(f"Mock: Releasing key {key}")

        @staticmethod
        def press(key):
            """Mock press method."""
            logging.getLogger(__name__).info(f"Mock: Pressing and releasing key {key}")

        @staticmethod
        def write(text):
            """Mock write method."""
            logging.getLogger(__name__).info(f"Mock: Typing text '{text}'")

        @staticmethod
        def hotkey(*keys):
            """Mock hotkey method."""
            logging.getLogger(__name__).info(f"Mock: Pressing hotkey {'+'.join(keys)}")

    # Use the mock implementation
    pyautogui = MockPyAutoGUI()

from .base import InputDevice, DeviceStatus


class KeyboardDevice(InputDevice):
    """
    Keyboard device implementation.
    """

    def __init__(
        self, device_id: str, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize keyboard device.

        Args:
            device_id: Unique device identifier
            name: Device name
            metadata: Additional device information
        """
        super().__init__(
            device_id=device_id, name=name, device_type="keyboard", metadata=metadata
        )
        self.logger = logging.getLogger(__name__)

        # Keyboard-specific attributes
        self.pressed_keys: Set[str] = set()  # Currently pressed keys
        self.layout = metadata.get("layout", "us") if metadata else "us"
        self.modifiers = {
            "shift": False,
            "ctrl": False,
            "alt": False,
            "meta": False,  # Windows key / Command key
        }

    async def key_down(self, key: str) -> Dict[str, Any]:
        """
        Press and hold a key.

        Args:
            key: Key to press

        Returns:
            Key press operation result
        """
        try:
            self.logger.info(f"Pressing key: {key}")

            # Press the physical key using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.keyDown(key)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating key down for {key}"
                )

            # Handle modifier keys
            if key.lower() in self.modifiers:
                self.modifiers[key.lower()] = True

            # Add to pressed keys
            self.pressed_keys.add(key)

            return {
                "status": "success",
                "device_id": self.device_id,
                "key": key,
                "state": "down",
            }
        except Exception as e:
            self.logger.error(f"Key down failed: {e}")
            return {"error": str(e)}

    async def key_up(self, key: str) -> Dict[str, Any]:
        """
        Release a key.

        Args:
            key: Key to release

        Returns:
            Key release operation result
        """
        try:
            self.logger.info(f"Releasing key: {key}")

            # Release the physical key using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.keyUp(key)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating key up for {key}"
                )

            # Handle modifier keys
            if key.lower() in self.modifiers:
                self.modifiers[key.lower()] = False

            # Remove from pressed keys
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)

            return {
                "status": "success",
                "device_id": self.device_id,
                "key": key,
                "state": "up",
            }
        except Exception as e:
            self.logger.error(f"Key up failed: {e}")
            return {"error": str(e)}

    async def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press and release a key.

        Args:
            key: Key to press

        Returns:
            Key press operation result
        """
        try:
            self.logger.info(f"Pressing and releasing key: {key}")

            # Use key_down and key_up methods
            down_result = await self.key_down(key)
            if "error" in down_result:
                return down_result

            up_result = await self.key_up(key)
            if "error" in up_result:
                return up_result

            # Also perform the physical key press using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.press(key)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating key press for {key}"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "key": key,
            }
        except Exception as e:
            self.logger.error(f"Key press failed: {e}")
            return {"error": str(e)}

    async def type_text(self, text: str) -> Dict[str, Any]:
        """
        Type a sequence of characters.

        Args:
            text: Text to type

        Returns:
            Text typing operation result
        """
        try:
            self.logger.info(f"Typing text: {text}")

            # Use press_key method for each character
            for char in text:
                result = await self.press_key(char)
                if "error" in result:
                    return result

            # Also type the text using PyAutoGUI for physical keyboard if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.write(text)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating typing text '{text}'"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "text": text,
                "length": len(text),
            }
        except Exception as e:
            self.logger.error(f"Text typing failed: {e}")
            return {"error": str(e)}

    async def press_hotkey(self, *keys: str) -> Dict[str, Any]:
        """
        Press a combination of keys simultaneously.

        Args:
            *keys: Keys to press in combination

        Returns:
            Hotkey operation result
        """
        try:
            key_list = list(keys)
            self.logger.info(f"Pressing hotkey: {'+'.join(key_list)}")

            # Press all keys in sequence
            for key in key_list:
                down_result = await self.key_down(key)
                if "error" in down_result:
                    # If there's an error, try to release any keys that were pressed
                    for k in reversed(key_list[: key_list.index(key)]):
                        await self.key_up(k)
                    return down_result

            # Release keys in reverse order
            for key in reversed(key_list):
                up_result = await self.key_up(key)
                if "error" in up_result:
                    return up_result

            # Also perform the physical hotkey press using PyAutoGUI if available
            if PYAUTOGUI_AVAILABLE:
                pyautogui.hotkey(*key_list)
            else:
                self.logger.info(
                    f"PyAutoGUI not available, simulating hotkey press {'+'.join(key_list)}"
                )

            return {
                "status": "success",
                "device_id": self.device_id,
                "hotkey": key_list,
            }
        except Exception as e:
            self.logger.error(f"Hotkey press failed: {e}")
            return {"error": str(e)}

    async def release_all_keys(self) -> Dict[str, Any]:
        """
        Release all currently pressed keys.

        Returns:
            Operation result
        """
        try:
            self.logger.info("Releasing all keys")

            # Make a copy of pressed_keys to avoid modification during iteration
            keys_to_release = list(self.pressed_keys)

            # Release all keys
            for key in keys_to_release:
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.keyUp(key)
                else:
                    self.logger.info(
                        f"PyAutoGUI not available, simulating key up for {key}"
                    )
                self.pressed_keys.remove(key)

            # Reset modifiers
            for mod in self.modifiers:
                self.modifiers[mod] = False
                # Make sure modifier keys are released if PyAutoGUI is available
                if PYAUTOGUI_AVAILABLE:
                    try:
                        pyautogui.keyUp(mod)
                    except Exception:
                        pass

            return {
                "status": "success",
                "device_id": self.device_id,
                "released_keys": keys_to_release,
            }
        except Exception as e:
            self.logger.error(f"Release all keys failed: {e}")
            return {"error": str(e)}

    async def connect(self) -> bool:
        """
        Connect to the keyboard device.

        Returns:
            Connection status
        """
        try:
            # Simulated connection logic
            await asyncio.sleep(0.5)
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Keyboard {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Keyboard connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the keyboard device.

        Returns:
            Disconnection status
        """
        try:
            # Release any pressed keys before disconnecting
            await self.release_all_keys()

            # Simulated disconnection logic
            await asyncio.sleep(0.3)
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Keyboard {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Keyboard disconnection failed: {e}")
            return False

    async def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on the keyboard device.

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
            if command == "key_down":
                key = params.get("key")
                if not key:
                    raise ValueError("Key parameter is required")
                return await self.key_down(key)
            elif command == "key_up":
                key = params.get("key")
                if not key:
                    raise ValueError("Key parameter is required")
                return await self.key_up(key)
            elif command == "press_key":
                key = params.get("key")
                if not key:
                    raise ValueError("Key parameter is required")
                return await self.press_key(key)
            elif command == "type_text":
                text = params.get("text")
                if not text:
                    raise ValueError("Text parameter is required")
                return await self.type_text(text)
            elif command == "press_hotkey":
                keys = params.get("keys", [])
                if not keys or not isinstance(keys, list):
                    raise ValueError("Keys parameter must be a non-empty list")
                return await self.press_hotkey(*keys)
            elif command == "release_all_keys":
                return await self.release_all_keys()
            else:
                raise ValueError(f"Unsupported command: {command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
