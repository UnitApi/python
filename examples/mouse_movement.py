"""
Example demonstrating how to control the physical mouse to move in different directions by small amounts using UnitAPI.
"""

import asyncio
import logging
import pyautogui
from unitapi.devices import MouseDevice


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def mouse_movement_example():
    """Demonstrate moving the mouse in different directions by small amounts."""
    logger.info("=== Mouse Movement Example ===")

    # Create a mouse device
    mouse = MouseDevice(
        device_id="mouse_01",
        name="Virtual Mouse",
        metadata={"type": "optical"}
    )

    # Connect to the mouse
    await mouse.connect()

    try:
        # Get initial position using pyautogui
        initial_x, initial_y = pyautogui.position()
        logger.info(f"Initial mouse position: ({initial_x}, {initial_y})")

        # Move mouse up by a small amount
        logger.info("Moving mouse up")
        await mouse.move_relative(0, -20)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(0, -20)
        await asyncio.sleep(0.5)

        # Move mouse right by a small amount
        logger.info("Moving mouse right")
        await mouse.move_relative(20, 0)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(20, 0)
        await asyncio.sleep(0.5)

        # Move mouse down by a small amount
        logger.info("Moving mouse down")
        await mouse.move_relative(0, 20)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(0, 20)
        await asyncio.sleep(0.5)

        # Move mouse left by a small amount
        logger.info("Moving mouse left")
        await mouse.move_relative(-20, 0)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(-20, 0)
        await asyncio.sleep(0.5)

        # Move mouse diagonally (up-right) by a small amount
        logger.info("Moving mouse diagonally (up-right)")
        await mouse.move_relative(15, -15)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(15, -15)
        await asyncio.sleep(0.5)
        
        # Move mouse diagonally (down-left) by a small amount
        logger.info("Moving mouse diagonally (down-left)")
        await mouse.move_relative(-15, 15)
        # Update the actual mouse position with pyautogui
        pyautogui.moveRel(-15, 15)
        await asyncio.sleep(0.5)
        
        # Get final position using pyautogui
        final_x, final_y = pyautogui.position()
        logger.info(f"Final mouse position: ({final_x}, {final_y})")
        
    finally:
        # Always make sure to disconnect
        await mouse.disconnect()


async def main():
    """Run the mouse movement example."""
    try:
        # Pause for a moment to give user time to prepare
        logger.info("Starting in 2 seconds...")
        await asyncio.sleep(2)
        
        # Run the example
        await mouse_movement_example()
    except Exception as e:
        logger.error(f"Error in example: {e}")


if __name__ == "__main__":
    asyncio.run(main())
