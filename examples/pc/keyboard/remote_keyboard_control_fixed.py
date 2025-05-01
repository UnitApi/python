#!/usr/bin/env python3
"""
Remote Keyboard Control Example (Fixed Version)

This script demonstrates how to control a keyboard on a remote Raspberry Pi device
using connection details from a .env file.

This fixed version ensures that keyboard commands are only sent to the remote server
and not executed locally.
"""

import asyncio
import argparse
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from unitapi.core.client import UnitAPIClient


class RemoteKeyboardControlExample:
    def __init__(
            self,
            server_host: str,
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize remote keyboard control example.

        Args:
            server_host: UnitAPI server host (Raspberry Pi address)
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
        
        self.logger.info(f"Initialized client for remote host: {server_host}:{server_port}")

    async def list_remote_keyboards(self) -> list:
        """
        List available keyboards on the remote device.

        Returns:
            List of keyboard devices
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
                self.logger.info(f"Found {len(keyboards)} keyboard(s) on remote device")
                for i, keyboard in enumerate(keyboards):
                    self.logger.info(f"Keyboard {i+1}: {keyboard.get('name')} (ID: {keyboard.get('device_id')})")
            else:
                self.logger.warning("No keyboards found on remote device")
                
            return keyboards
            
        except Exception as e:
            self.logger.error(f"Failed to list remote keyboards: {e}")
            return []

    async def type_text(self, device_id: str, text: str) -> Dict[str, Any]:
        """
        Type text on a remote keyboard.

        Args:
            device_id: Keyboard device ID
            text: Text to type

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Typing text '{text}' on remote keyboard {device_id}...")
            
            # Execute type_text command
            result = await self.client.execute_command(
                device_id=device_id,
                command='type_text',
                params={'text': text}
            )
            
            if 'error' in result:
                self.logger.error(f"Typing failed: {result['error']}")
                return result
                
            self.logger.info("Text typed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to type text on remote keyboard: {e}")
            return {'error': str(e)}

    async def press_key(self, device_id: str, key: str) -> Dict[str, Any]:
        """
        Press a key on a remote keyboard.

        Args:
            device_id: Keyboard device ID
            key: Key to press (e.g., 'enter', 'space', 'a', etc.)

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Pressing key '{key}' on remote keyboard {device_id}...")
            
            # Execute press_key command
            result = await self.client.execute_command(
                device_id=device_id,
                command='press_key',
                params={'key': key}
            )
            
            if 'error' in result:
                self.logger.error(f"Key press failed: {result['error']}")
                return result
                
            self.logger.info(f"Key '{key}' pressed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press key on remote keyboard: {e}")
            return {'error': str(e)}

    async def press_hotkey(self, device_id: str, *keys) -> Dict[str, Any]:
        """
        Press a hotkey combination on a remote keyboard.

        Args:
            device_id: Keyboard device ID
            *keys: Keys to press together (e.g., 'ctrl', 's')

        Returns:
            Command result
        """
        try:
            key_str = '+'.join(keys)
            self.logger.info(f"Pressing hotkey '{key_str}' on remote keyboard {device_id}...")
            
            # Execute press_hotkey command
            result = await self.client.execute_command(
                device_id=device_id,
                command='press_hotkey',
                params={'keys': list(keys)}
            )
            
            if 'error' in result:
                self.logger.error(f"Hotkey press failed: {result['error']}")
                return result
                
            self.logger.info(f"Hotkey '{key_str}' pressed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press hotkey on remote keyboard: {e}")
            return {'error': str(e)}


async def main():
    """
    Run the remote keyboard control example.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Raspberry Pi connection details from .env
    rpi_host = os.getenv('RPI_HOST', '192.168.1.100')
    rpi_user = os.getenv('RPI_USER', 'pi')
    rpi_password = os.getenv('RPI_PASSWORD', 'raspberry')
    
    # Display connection details from .env
    print("=== Connection Details from .env ===")
    print(f"Host: {rpi_host}")
    print(f"User: {rpi_user}")
    print(f"Password: {'*' * len(rpi_password)}")
    print("===================================")
    
    parser = argparse.ArgumentParser(description='Remote Keyboard Control Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default=rpi_host, help='Remote UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='Remote UnitAPI server port')
    parser.add_argument('--list', action='store_true', help='List available remote keyboards')
    parser.add_argument('--device-id', help='Specific remote keyboard device ID to use')
    parser.add_argument('--text', help='Text to type on the remote keyboard')
    parser.add_argument('--key', help='Key to press on the remote keyboard')
    parser.add_argument('--hotkey', help='Hotkey to press (comma-separated keys, e.g., ctrl,s)')
    parser.add_argument('--check-connection', action='store_true', help='Check connection to the remote server')
    
    args = parser.parse_args()
    
    # Create the client
    example = RemoteKeyboardControlExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Check connection if requested
    if args.check_connection:
        try:
            print(f"Checking connection to {args.host}:{args.port}...")
            # Try to list devices to check connection
            devices = await example.client.list_devices()
            print(f"Connection successful! Found {len(devices)} devices.")
            return
        except Exception as e:
            print(f"Connection failed: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure the Raspberry Pi is powered on and connected to the network")
            print("2. Verify that the UnitAPI server is running on the Raspberry Pi")
            print("3. Check that the IP address and port are correct")
            print("4. Ensure there are no firewalls blocking the connection")
            print("\nYou can try to SSH into the Raspberry Pi to check its status:")
            print(f"  python scripts/ssh_connect_wrapper.sh {rpi_user}@{rpi_host} {rpi_password}")
            return
    
    if args.list:
        # List available remote keyboards
        keyboards = await example.list_remote_keyboards()
        if not keyboards:
            print("\nNo keyboards found on the remote device.")
            print("Make sure the keyboard server is running on the Raspberry Pi:")
            print(f"  python scripts/ssh_connect_wrapper.sh {rpi_user}@{rpi_host} {rpi_password} -c 'systemctl status unitapi-keyboard.service'")
    elif args.device_id:
        if args.text:
            # Type text
            await example.type_text(
                device_id=args.device_id,
                text=args.text
            )
        elif args.key:
            # Press key
            await example.press_key(
                device_id=args.device_id,
                key=args.key
            )
        elif args.hotkey:
            # Press hotkey
            keys = args.hotkey.split(',')
            await example.press_hotkey(
                device_id=args.device_id,
                *keys
            )
        else:
            print("Please specify an action: --text, --key, or --hotkey")
    else:
        # List keyboards and use the first one for a demo
        keyboards = await example.list_remote_keyboards()
        
        if keyboards:
            # Use the first keyboard
            keyboard = keyboards[0]
            device_id = keyboard.get('device_id')
            
            # Demo sequence
            print("\n=== Running keyboard demo sequence ===")
            
            # Type text
            await example.type_text(
                device_id=device_id,
                text="Hello from UnitAPI remote keyboard!"
            )
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Press Enter
            await example.press_key(
                device_id=device_id,
                key="enter"
            )
            
            # Wait a bit
            await asyncio.sleep(1.0)
            
            # Type more text
            await example.type_text(
                device_id=device_id,
                text="This is a remote keyboard control demo."
            )
            
            # Press a hotkey
            await asyncio.sleep(1.0)
            await example.press_hotkey(
                device_id=device_id,
                *["ctrl", "a"]
            )
            
            print("Demo sequence completed!")
        else:
            print("No remote keyboards available. Make sure the UnitAPI server is running on the Raspberry Pi.")
            print("You can check the server status with:")
            print(f"  python scripts/ssh_connect_wrapper.sh {rpi_user}@{rpi_host} {rpi_password} -c 'systemctl status unitapi-keyboard.service'")
            print("\nIf the service is not running, you can start it with:")
            print(f"  python scripts/ssh_connect_wrapper.sh {rpi_user}@{rpi_host} {rpi_password} -c 'sudo systemctl start unitapi-keyboard.service'")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your network connection")
        print("2. Verify that the Raspberry Pi is powered on and connected to the network")
        print("3. Make sure the UnitAPI server is running on the Raspberry Pi")
        print("4. Check the .env file for correct connection details")
