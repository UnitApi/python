#!/usr/bin/env python3
"""
Raspberry Pi Keyboard Client Example

This script demonstrates how to control a keyboard on a Raspberry Pi using UnitAPI.
It shows how to type text, press keys, and use keyboard shortcuts.
"""

import asyncio
import argparse
import logging
import time
from typing import Dict, Any, List, Optional

from unitapi.core.client import UnitAPIClient


class RPiKeyboardExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Keyboard example.

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
        
        # Keyboard device ID
        self.keyboard_device_id = None

    async def discover_keyboard(self) -> bool:
        """
        Discover Raspberry Pi Keyboard.

        Returns:
            Success status
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for keyboard devices
            keyboards = [
                device for device in devices
                if device.get('type') == 'keyboard'
            ]
            
            if keyboards:
                self.logger.info(f"Found {len(keyboards)} keyboard(s)")
                for i, kbd in enumerate(keyboards):
                    kbd_type = kbd.get('metadata', {}).get('device_type', 'unknown')
                    self.logger.info(f"Keyboard {i+1}: {kbd.get('name')} ({kbd_type}) (ID: {kbd.get('device_id')})")
                
                # Look for Raspberry Pi keyboard specifically
                rpi_keyboards = [
                    kbd for kbd in keyboards
                    if 'raspberry' in kbd.get('name', '').lower() or 
                       'rpi' in kbd.get('name', '').lower() or
                       'raspberry' in str(kbd.get('metadata', {})).lower() or
                       'rpi' in str(kbd.get('metadata', {})).lower()
                ]
                
                if rpi_keyboards:
                    # Use the first Raspberry Pi keyboard
                    self.keyboard_device_id = rpi_keyboards[0].get('device_id')
                    self.logger.info(f"Using Raspberry Pi Keyboard: {rpi_keyboards[0].get('name')}")
                else:
                    # Use the first available keyboard
                    self.keyboard_device_id = keyboards[0].get('device_id')
                    self.logger.info(f"No specific Raspberry Pi Keyboard found. Using: {keyboards[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No keyboards found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover keyboard: {e}")
            return False

    async def type_text(self, text: str) -> Dict[str, Any]:
        """
        Type text on the Raspberry Pi Keyboard.

        Args:
            text: Text to type

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Typing text: '{text}'")
            
            # Execute type_text command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='type_text',
                params={'text': text}
            )
            
            if 'error' in result:
                self.logger.error(f"Typing failed: {result['error']}")
                return result
                
            self.logger.info("Text typed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to type text: {e}")
            return {'error': str(e), 'status': 'error'}

    async def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press a key on the Raspberry Pi Keyboard.

        Args:
            key: Key to press (e.g., 'enter', 'space', 'a', etc.)

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Pressing key: '{key}'")
            
            # Execute press_key command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='press_key',
                params={'key': key}
            )
            
            if 'error' in result:
                self.logger.error(f"Key press failed: {result['error']}")
                return result
                
            self.logger.info(f"Key '{key}' pressed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press key: {e}")
            return {'error': str(e), 'status': 'error'}

    async def press_hotkey(self, *keys) -> Dict[str, Any]:
        """
        Press a hotkey combination on the Raspberry Pi Keyboard.

        Args:
            *keys: Keys to press together (e.g., 'ctrl', 's')

        Returns:
            Command result
        """
        try:
            key_str = '+'.join(keys)
            self.logger.info(f"Pressing hotkey: '{key_str}'")
            
            # Execute press_hotkey command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='press_hotkey',
                params={'keys': list(keys)}
            )
            
            if 'error' in result:
                self.logger.error(f"Hotkey press failed: {result['error']}")
                return result
                
            self.logger.info(f"Hotkey '{key_str}' pressed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press hotkey: {e}")
            return {'error': str(e), 'status': 'error'}

    async def key_down(self, key: str) -> Dict[str, Any]:
        """
        Press and hold a key on the Raspberry Pi Keyboard.

        Args:
            key: Key to press and hold

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Pressing key down: '{key}'")
            
            # Execute key_down command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='key_down',
                params={'key': key}
            )
            
            if 'error' in result:
                self.logger.error(f"Key down failed: {result['error']}")
                return result
                
            self.logger.info(f"Key '{key}' pressed down successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press key down: {e}")
            return {'error': str(e), 'status': 'error'}

    async def key_up(self, key: str) -> Dict[str, Any]:
        """
        Release a key on the Raspberry Pi Keyboard.

        Args:
            key: Key to release

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Releasing key: '{key}'")
            
            # Execute key_up command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='key_up',
                params={'key': key}
            )
            
            if 'error' in result:
                self.logger.error(f"Key up failed: {result['error']}")
                return result
                
            self.logger.info(f"Key '{key}' released successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to release key: {e}")
            return {'error': str(e), 'status': 'error'}

    async def release_all_keys(self) -> Dict[str, Any]:
        """
        Release all keys on the Raspberry Pi Keyboard.

        Returns:
            Command result
        """
        try:
            self.logger.info("Releasing all keys")
            
            # Execute release_all_keys command
            result = await self.client.execute_command(
                device_id=self.keyboard_device_id,
                command='release_all_keys',
                params={}
            )
            
            if 'error' in result:
                self.logger.error(f"Release all keys failed: {result['error']}")
                return result
                
            self.logger.info("All keys released successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to release all keys: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_typing_demo(self) -> Dict[str, Any]:
        """
        Run a typing demo on the Raspberry Pi Keyboard.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Keyboard Typing Demo ===")
            
            # Type some text
            await self.type_text("Hello from UnitAPI Raspberry Pi Keyboard!")
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Press Enter
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Type more text
            await self.type_text("This is a demonstration of remote keyboard control.")
            
            # Press Enter
            await asyncio.sleep(0.5)
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Type text with special characters
            await self.type_text("Special characters: !@#$%^&*()")
            
            # Press Enter
            await asyncio.sleep(0.5)
            await self.press_key("enter")
            
            self.logger.info("Typing demo completed successfully")
            return {'status': 'success', 'message': 'Typing demo completed'}
            
        except Exception as e:
            self.logger.error(f"Typing demo failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_hotkey_demo(self) -> Dict[str, Any]:
        """
        Run a hotkey demo on the Raspberry Pi Keyboard.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Keyboard Hotkey Demo ===")
            
            # Type some text
            await self.type_text("This text will be selected with Ctrl+A")
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Press Ctrl+A to select all
            await self.press_hotkey("ctrl", "a")
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Press Delete to clear
            await self.press_key("delete")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Type new text
            await self.type_text("Common hotkeys:")
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Type hotkey examples
            await self.type_text("- Ctrl+C (Copy)")
            await self.press_key("enter")
            
            await asyncio.sleep(0.3)
            await self.type_text("- Ctrl+V (Paste)")
            await self.press_key("enter")
            
            await asyncio.sleep(0.3)
            await self.type_text("- Ctrl+S (Save)")
            await self.press_key("enter")
            
            await asyncio.sleep(0.3)
            await self.type_text("- Alt+Tab (Switch windows)")
            await self.press_key("enter")
            
            self.logger.info("Hotkey demo completed successfully")
            return {'status': 'success', 'message': 'Hotkey demo completed'}
            
        except Exception as e:
            self.logger.error(f"Hotkey demo failed: {e}")
            # Make sure to release all keys in case of error
            await self.release_all_keys()
            return {'error': str(e), 'status': 'error'}

    async def run_key_sequence_demo(self) -> Dict[str, Any]:
        """
        Run a key sequence demo on the Raspberry Pi Keyboard.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Keyboard Key Sequence Demo ===")
            
            # Type some text
            await self.type_text("Arrow key demonstration:")
            
            # Press Enter
            await asyncio.sleep(0.5)
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Press arrow keys in sequence
            for direction in ["up", "right", "down", "left"]:
                self.logger.info(f"Pressing {direction} arrow key")
                await self.press_key(direction)
                await asyncio.sleep(0.5)
            
            # Press Enter
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Type text about modifier keys
            await self.type_text("Modifier key demonstration:")
            
            # Press Enter
            await asyncio.sleep(0.5)
            await self.press_key("enter")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            # Demonstrate Shift key for uppercase
            await self.key_down("shift")
            await self.type_text("THIS TEXT IS TYPED WITH SHIFT HELD DOWN")
            await self.key_up("shift")
            
            # Press Enter
            await asyncio.sleep(0.5)
            await self.press_key("enter")
            
            self.logger.info("Key sequence demo completed successfully")
            return {'status': 'success', 'message': 'Key sequence demo completed'}
            
        except Exception as e:
            self.logger.error(f"Key sequence demo failed: {e}")
            # Make sure to release all keys in case of error
            await self.release_all_keys()
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi Keyboard example.
    """
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Keyboard Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--demo', choices=['typing', 'hotkey', 'sequence', 'all'], 
                        default='typing', help='Demo to run')
    parser.add_argument('--text', help='Text to type (for custom commands)')
    parser.add_argument('--key', help='Key to press (for custom commands)')
    parser.add_argument('--hotkey', help='Hotkey to press (comma-separated keys, e.g., ctrl,s)')
    
    args = parser.parse_args()
    
    example = RPiKeyboardExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover keyboard
    if not await example.discover_keyboard():
        print("Failed to discover Raspberry Pi Keyboard. Make sure the UnitAPI server is running.")
        return
    
    # Run custom commands if specified
    if args.text:
        await example.type_text(args.text)
    elif args.key:
        await example.press_key(args.key)
    elif args.hotkey:
        keys = args.hotkey.split(',')
        await example.press_hotkey(*keys)
    else:
        # Run the selected demo
        if args.demo == 'typing' or args.demo == 'all':
            await example.run_typing_demo()
            
        if args.demo == 'hotkey' or args.demo == 'all':
            if args.demo == 'all':
                await asyncio.sleep(1.0)
            await example.run_hotkey_demo()
            
        if args.demo == 'sequence' or args.demo == 'all':
            if args.demo == 'all':
                await asyncio.sleep(1.0)
            await example.run_key_sequence_demo()
    
    # Always release all keys at the end
    await example.release_all_keys()


if __name__ == "__main__":
    asyncio.run(main())
