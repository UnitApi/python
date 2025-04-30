"""
Example demonstrating how to control the physical mouse to move in different directions by small amounts using PyAutoGUI.
"""

import time
import logging
import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def mouse_movement_example():
    """Demonstrate moving the physical mouse in different directions by small amounts."""
    logger.info("=== Mouse Movement Example with PyAutoGUI ===")
    
    # Get initial position
    initial_x, initial_y = pyautogui.position()
    logger.info(f"Initial mouse position: ({initial_x}, {initial_y})")
    
    # Move mouse up by a small amount
    logger.info("Moving mouse up")
    pyautogui.moveRel(0, -20)
    time.sleep(0.5)
    
    # Move mouse right by a small amount
    logger.info("Moving mouse right")
    pyautogui.moveRel(20, 0)
    time.sleep(0.5)
    
    # Move mouse down by a small amount
    logger.info("Moving mouse down")
    pyautogui.moveRel(0, 20)
    time.sleep(0.5)
    
    # Move mouse left by a small amount
    logger.info("Moving mouse left")
    pyautogui.moveRel(-20, 0)
    time.sleep(0.5)
    
    # Move mouse diagonally (up-right) by a small amount
    logger.info("Moving mouse diagonally (up-right)")
    pyautogui.moveRel(15, -15)
    time.sleep(0.5)
    
    # Move mouse diagonally (down-left) by a small amount
    logger.info("Moving mouse diagonally (down-left)")
    pyautogui.moveRel(-15, 15)
    time.sleep(0.5)
    
    # Get final position
    final_x, final_y = pyautogui.position()
    logger.info(f"Final mouse position: ({final_x}, {final_y})")


if __name__ == "__main__":
    try:
        # Pause for a moment to give user time to prepare
        logger.info("Starting in 2 seconds...")
        time.sleep(2)
        
        # Run the example
        mouse_movement_example()
    except Exception as e:
        logger.error(f"Error in example: {e}")
