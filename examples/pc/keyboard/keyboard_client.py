"""
Example demonstrating how to control a local keyboard to type text and press Enter.
"""

import asyncio
import logging
from unitapi.devices import KeyboardDevice


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def keyboard_text_input_example():
    """Demonstrate typing text and pressing Enter with the keyboard device."""
    logger.info("=== Keyboard Text Input Example ===")
    
    # Create a keyboard device
    keyboard = KeyboardDevice(
        device_id="keyboard_01",
        name="Virtual Keyboard",
        metadata={"layout": "us"}
    )
    
    # Connect to the keyboard
    await keyboard.connect()
    
    try:
        # Type some text
        text_to_type = "Hello"
        logger.info(f"Typing text: '{text_to_type}'")
        await keyboard.type_text(text_to_type)
        
        # Small pause before pressing Enter
        await asyncio.sleep(0.5)
        
        # Press Enter key
        logger.info("Pressing Enter key")
        await keyboard.press_key("enter")
        
        # You can also type and press Enter in a sequence
        await asyncio.sleep(1.0)  # Wait a bit before the next action
        
        second_text = "1234"
        logger.info(f"Typing second text: '{second_text}'")
        await keyboard.type_text(second_text)
        await keyboard.press_key("enter")
        
        # Example of typing with special keys
        await asyncio.sleep(1.0)
        logger.info("Typing with special keys")
        
        # Hold shift to type uppercase
        await keyboard.key_down("shift")
        await keyboard.type_text("text")
        await keyboard.key_up("shift")
        await keyboard.press_key("enter")
        
        # Type text and press keyboard shortcut
        await asyncio.sleep(1.0)
        await keyboard.type_text("Saving with Ctrl+S shortcut")
        await asyncio.sleep(0.5)
        await keyboard.press_hotkey("ctrl", "s")
        
    finally:
        # Always make sure to release all keys and disconnect
        await keyboard.release_all_keys()
        await keyboard.disconnect()


async def main():
    """Run the keyboard text input example."""
    try:
        await keyboard_text_input_example()
    except Exception as e:
        logger.error(f"Error in example: {e}")


if __name__ == "__main__":
    asyncio.run(main())
