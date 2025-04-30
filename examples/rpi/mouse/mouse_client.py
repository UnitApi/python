#!/usr/bin/env python3
"""
Raspberry Pi Mouse Client Example

This script demonstrates how to control a mouse on a Raspberry Pi using UnitAPI.
It shows how to move the mouse, click, scroll, and perform drag operations.
"""

import asyncio
import argparse
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from unitapi.core.client import UnitAPIClient


class RPiMouseExample:
    def __init__(
            self,
            server_host: str = 'localhost',
            server_port: int = 7890,
            debug: bool = False
    ):
        """
        Initialize Raspberry Pi Mouse example.

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
        
        # Mouse device ID
        self.mouse_device_id = None

    async def discover_mouse(self) -> bool:
        """
        Discover Raspberry Pi Mouse.

        Returns:
            Success status
        """
        try:
            # Get all devices
            devices = await self.client.list_devices()
            
            # Filter for mouse devices
            mice = [
                device for device in devices
                if device.get('type') == 'mouse'
            ]
            
            if mice:
                self.logger.info(f"Found {len(mice)} mouse device(s)")
                for i, mouse in enumerate(mice):
                    mouse_type = mouse.get('metadata', {}).get('device_type', 'unknown')
                    self.logger.info(f"Mouse {i+1}: {mouse.get('name')} ({mouse_type}) (ID: {mouse.get('device_id')})")
                
                # Look for Raspberry Pi mouse specifically
                rpi_mice = [
                    mouse for mouse in mice
                    if 'raspberry' in mouse.get('name', '').lower() or 
                       'rpi' in mouse.get('name', '').lower() or
                       'raspberry' in str(mouse.get('metadata', {})).lower() or
                       'rpi' in str(mouse.get('metadata', {})).lower()
                ]
                
                if rpi_mice:
                    # Use the first Raspberry Pi mouse
                    self.mouse_device_id = rpi_mice[0].get('device_id')
                    self.logger.info(f"Using Raspberry Pi Mouse: {rpi_mice[0].get('name')}")
                else:
                    # Use the first available mouse
                    self.mouse_device_id = mice[0].get('device_id')
                    self.logger.info(f"No specific Raspberry Pi Mouse found. Using: {mice[0].get('name')}")
                
                return True
            else:
                self.logger.warning("No mouse devices found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to discover mouse: {e}")
            return False

    async def move_to(self, x: int, y: int) -> Dict[str, Any]:
        """
        Move mouse to absolute position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Moving mouse to position ({x}, {y})")
            
            # Execute move_to command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='move_to',
                params={'x': x, 'y': y}
            )
            
            if 'error' in result:
                self.logger.error(f"Move to failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse moved to ({x}, {y}) successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to move mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def move_relative(self, dx: int, dy: int) -> Dict[str, Any]:
        """
        Move mouse by a relative amount.

        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Moving mouse by ({dx}, {dy})")
            
            # Execute move_relative command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='move_relative',
                params={'dx': dx, 'dy': dy}
            )
            
            if 'error' in result:
                self.logger.error(f"Move relative failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse moved by ({dx}, {dy}) successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to move mouse relatively: {e}")
            return {'error': str(e), 'status': 'error'}

    async def click(self, button: str = 'left') -> Dict[str, Any]:
        """
        Perform a mouse click.

        Args:
            button: Mouse button to click ('left', 'right', 'middle')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Clicking {button} mouse button")
            
            # Execute click command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='click',
                params={'button': button}
            )
            
            if 'error' in result:
                self.logger.error(f"Click failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse {button} button clicked successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to click mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def double_click(self, button: str = 'left') -> Dict[str, Any]:
        """
        Perform a mouse double-click.

        Args:
            button: Mouse button to double-click ('left', 'right', 'middle')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Double-clicking {button} mouse button")
            
            # Execute double_click command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='double_click',
                params={'button': button}
            )
            
            if 'error' in result:
                self.logger.error(f"Double-click failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse {button} button double-clicked successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to double-click mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def button_down(self, button: str = 'left') -> Dict[str, Any]:
        """
        Press and hold a mouse button.

        Args:
            button: Mouse button to press ('left', 'right', 'middle')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Pressing {button} mouse button down")
            
            # Execute button_down command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='button_down',
                params={'button': button}
            )
            
            if 'error' in result:
                self.logger.error(f"Button down failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse {button} button pressed down successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to press mouse button down: {e}")
            return {'error': str(e), 'status': 'error'}

    async def button_up(self, button: str = 'left') -> Dict[str, Any]:
        """
        Release a mouse button.

        Args:
            button: Mouse button to release ('left', 'right', 'middle')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Releasing {button} mouse button")
            
            # Execute button_up command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='button_up',
                params={'button': button}
            )
            
            if 'error' in result:
                self.logger.error(f"Button up failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse {button} button released successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to release mouse button: {e}")
            return {'error': str(e), 'status': 'error'}

    async def scroll(self, amount: int) -> Dict[str, Any]:
        """
        Scroll the mouse wheel.

        Args:
            amount: Scroll amount (positive for up, negative for down)

        Returns:
            Command result
        """
        try:
            direction = "up" if amount > 0 else "down"
            self.logger.info(f"Scrolling {direction} by {abs(amount)}")
            
            # Execute scroll command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='scroll',
                params={'amount': amount}
            )
            
            if 'error' in result:
                self.logger.error(f"Scroll failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse scrolled {direction} successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to scroll mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def drag(self, x: int, y: int, button: str = 'left') -> Dict[str, Any]:
        """
        Perform a drag operation to target position.

        Args:
            x: Target X coordinate
            y: Target Y coordinate
            button: Mouse button to use for dragging ('left', 'right', 'middle')

        Returns:
            Command result
        """
        try:
            self.logger.info(f"Dragging with {button} button to position ({x}, {y})")
            
            # Execute drag command
            result = await self.client.execute_command(
                device_id=self.mouse_device_id,
                command='drag',
                params={'x': x, 'y': y, 'button': button}
            )
            
            if 'error' in result:
                self.logger.error(f"Drag failed: {result['error']}")
                return result
                
            self.logger.info(f"Mouse dragged to ({x}, {y}) successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to drag mouse: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_movement_demo(self) -> Dict[str, Any]:
        """
        Run a mouse movement demo.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Mouse Movement Demo ===")
            
            # Get current screen resolution (assuming 1920x1080 for demo)
            screen_width, screen_height = 1920, 1080
            
            # Move to center of screen
            center_x, center_y = screen_width // 2, screen_height // 2
            await self.move_to(center_x, center_y)
            await asyncio.sleep(1.0)
            
            # Move in a square pattern
            square_size = 100
            
            # Move up
            await self.move_relative(0, -square_size)
            await asyncio.sleep(0.5)
            
            # Move right
            await self.move_relative(square_size, 0)
            await asyncio.sleep(0.5)
            
            # Move down
            await self.move_relative(0, square_size)
            await asyncio.sleep(0.5)
            
            # Move left
            await self.move_relative(-square_size, 0)
            await asyncio.sleep(0.5)
            
            # Move in a circle pattern
            self.logger.info("Moving in a circle pattern")
            radius = 100
            steps = 36  # Number of steps to complete the circle
            
            for i in range(steps):
                # Calculate position on circle
                angle = 2 * 3.14159 * i / steps
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                
                # Move to position on circle
                await self.move_to(x, y)
                await asyncio.sleep(0.1)
            
            # Return to center
            await self.move_to(center_x, center_y)
            
            self.logger.info("Movement demo completed successfully")
            return {'status': 'success', 'message': 'Movement demo completed'}
            
        except Exception as e:
            self.logger.error(f"Movement demo failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_click_demo(self) -> Dict[str, Any]:
        """
        Run a mouse click demo.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Mouse Click Demo ===")
            
            # Get current screen resolution (assuming 1920x1080 for demo)
            screen_width, screen_height = 1920, 1080
            
            # Move to center of screen
            center_x, center_y = screen_width // 2, screen_height // 2
            await self.move_to(center_x, center_y)
            await asyncio.sleep(1.0)
            
            # Left click
            self.logger.info("Performing left click")
            await self.click('left')
            await asyncio.sleep(1.0)
            
            # Right click
            self.logger.info("Performing right click")
            await self.click('right')
            await asyncio.sleep(1.0)
            
            # Double click
            self.logger.info("Performing double click")
            await self.double_click('left')
            await asyncio.sleep(1.0)
            
            # Button down and up
            self.logger.info("Demonstrating button down and up")
            await self.button_down('left')
            await asyncio.sleep(1.0)
            await self.button_up('left')
            
            self.logger.info("Click demo completed successfully")
            return {'status': 'success', 'message': 'Click demo completed'}
            
        except Exception as e:
            self.logger.error(f"Click demo failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_scroll_demo(self) -> Dict[str, Any]:
        """
        Run a mouse scroll demo.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Mouse Scroll Demo ===")
            
            # Get current screen resolution (assuming 1920x1080 for demo)
            screen_width, screen_height = 1920, 1080
            
            # Move to center of screen
            center_x, center_y = screen_width // 2, screen_height // 2
            await self.move_to(center_x, center_y)
            await asyncio.sleep(1.0)
            
            # Scroll down
            self.logger.info("Scrolling down")
            for _ in range(5):
                await self.scroll(-3)
                await asyncio.sleep(0.3)
            
            await asyncio.sleep(1.0)
            
            # Scroll up
            self.logger.info("Scrolling up")
            for _ in range(5):
                await self.scroll(3)
                await asyncio.sleep(0.3)
            
            self.logger.info("Scroll demo completed successfully")
            return {'status': 'success', 'message': 'Scroll demo completed'}
            
        except Exception as e:
            self.logger.error(f"Scroll demo failed: {e}")
            return {'error': str(e), 'status': 'error'}

    async def run_drag_demo(self) -> Dict[str, Any]:
        """
        Run a mouse drag demo.

        Returns:
            Demo result
        """
        try:
            self.logger.info("=== Running Mouse Drag Demo ===")
            
            # Get current screen resolution (assuming 1920x1080 for demo)
            screen_width, screen_height = 1920, 1080
            
            # Move to starting position
            start_x, start_y = screen_width // 4, screen_height // 2
            await self.move_to(start_x, start_y)
            await asyncio.sleep(1.0)
            
            # Drag to ending position
            end_x, end_y = (screen_width * 3) // 4, screen_height // 2
            self.logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            await self.drag(end_x, end_y, 'left')
            await asyncio.sleep(1.0)
            
            # Drag in a square pattern
            square_size = 100
            
            # Starting point for square
            square_x, square_y = screen_width // 2 - square_size // 2, screen_height // 2 - square_size // 2
            await self.move_to(square_x, square_y)
            await asyncio.sleep(0.5)
            
            # Press mouse button down
            await self.button_down('left')
            
            # Draw square by moving
            # Move right
            await self.move_relative(square_size, 0)
            await asyncio.sleep(0.5)
            
            # Move down
            await self.move_relative(0, square_size)
            await asyncio.sleep(0.5)
            
            # Move left
            await self.move_relative(-square_size, 0)
            await asyncio.sleep(0.5)
            
            # Move up
            await self.move_relative(0, -square_size)
            await asyncio.sleep(0.5)
            
            # Release mouse button
            await self.button_up('left')
            
            self.logger.info("Drag demo completed successfully")
            return {'status': 'success', 'message': 'Drag demo completed'}
            
        except Exception as e:
            self.logger.error(f"Drag demo failed: {e}")
            return {'error': str(e), 'status': 'error'}


async def main():
    """
    Run the Raspberry Pi Mouse example.
    """
    # Import math here to avoid global import issues
    import math
    
    parser = argparse.ArgumentParser(description='UnitAPI Raspberry Pi Mouse Example')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--host', default='localhost', help='UnitAPI server host')
    parser.add_argument('--port', type=int, default=7890, help='UnitAPI server port')
    parser.add_argument('--demo', choices=['movement', 'click', 'scroll', 'drag', 'all'], 
                        default='movement', help='Demo to run')
    parser.add_argument('--x', type=int, help='X coordinate for move_to command')
    parser.add_argument('--y', type=int, help='Y coordinate for move_to command')
    parser.add_argument('--dx', type=int, help='X delta for move_relative command')
    parser.add_argument('--dy', type=int, help='Y delta for move_relative command')
    parser.add_argument('--button', choices=['left', 'right', 'middle'], 
                        help='Mouse button for click commands')
    parser.add_argument('--scroll-amount', type=int, help='Scroll amount (positive for up, negative for down)')
    
    args = parser.parse_args()
    
    example = RPiMouseExample(
        server_host=args.host,
        server_port=args.port,
        debug=args.debug
    )
    
    # Discover mouse
    if not await example.discover_mouse():
        print("Failed to discover Raspberry Pi Mouse. Make sure the UnitAPI server is running.")
        return
    
    # Run custom commands if specified
    if args.x is not None and args.y is not None:
        await example.move_to(args.x, args.y)
    elif args.dx is not None and args.dy is not None:
        await example.move_relative(args.dx, args.dy)
    elif args.button is not None:
        await example.click(args.button)
    elif args.scroll_amount is not None:
        await example.scroll(args.scroll_amount)
    else:
        # Run the selected demo
        if args.demo == 'movement' or args.demo == 'all':
            await example.run_movement_demo()
            
        if args.demo == 'click' or args.demo == 'all':
            if args.demo == 'all':
                await asyncio.sleep(1.0)
            await example.run_click_demo()
            
        if args.demo == 'scroll' or args.demo == 'all':
            if args.demo == 'all':
                await asyncio.sleep(1.0)
            await example.run_scroll_demo()
            
        if args.demo == 'drag' or args.demo == 'all':
            if args.demo == 'all':
                await asyncio.sleep(1.0)
            await example.run_drag_demo()


if __name__ == "__main__":
    asyncio.run(main())
