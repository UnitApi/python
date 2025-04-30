"""
Example demonstrating the use of input devices (mouse, keyboard, touchscreen, gamepad).
"""

import asyncio
import logging
from unitapi.devices import (
    MouseDevice,
    KeyboardDevice,
    TouchscreenDevice,
    GamepadDevice,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def mouse_example():
    """Demonstrate mouse device functionality."""
    logger.info("=== Mouse Device Example ===")
    
    # Create a mouse device
    mouse = MouseDevice(
        device_id="mouse_01",
        name="Virtual Mouse",
        metadata={"dpi": 1200}
    )
    
    # Connect to the mouse
    await mouse.connect()
    
    # Move the mouse to an absolute position
    await mouse.move_to(500, 300)
    
    # Perform a left click
    await mouse.click()
    
    # Perform a right click
    await mouse.click(button="right")
    
    # Perform a double click
    await mouse.double_click()
    
    # Perform a drag operation
    await mouse.drag(700, 400)
    
    # Scroll the mouse wheel
    await mouse.scroll(5)  # Scroll up
    await mouse.scroll(-5)  # Scroll down
    
    # Move the mouse relatively
    await mouse.move_relative(100, 50)
    
    # Disconnect from the mouse
    await mouse.disconnect()


async def keyboard_example():
    """Demonstrate keyboard device functionality."""
    logger.info("=== Keyboard Device Example ===")
    
    # Create a keyboard device
    keyboard = KeyboardDevice(
        device_id="keyboard_01",
        name="Virtual Keyboard",
        metadata={"layout": "us"}
    )
    
    # Connect to the keyboard
    await keyboard.connect()
    
    # Type some text
    await keyboard.type_text("Hello, UnitAPI!")
    
    # Press individual keys
    await keyboard.press_key("a")
    await keyboard.press_key("b")
    await keyboard.press_key("c")
    
    # Press and hold a key
    await keyboard.key_down("shift")
    
    # Press another key while holding shift
    await keyboard.press_key("d")  # This will type "D" (uppercase)
    
    # Release the shift key
    await keyboard.key_up("shift")
    
    # Press a hotkey combination (Ctrl+C)
    await keyboard.press_hotkey("ctrl", "c")
    
    # Press another hotkey combination (Ctrl+V)
    await keyboard.press_hotkey("ctrl", "v")
    
    # Make sure all keys are released
    await keyboard.release_all_keys()
    
    # Disconnect from the keyboard
    await keyboard.disconnect()


async def touchscreen_example():
    """Demonstrate touchscreen device functionality."""
    logger.info("=== Touchscreen Device Example ===")
    
    # Create a touchscreen device
    touchscreen = TouchscreenDevice(
        device_id="touchscreen_01",
        name="Virtual Touchscreen",
        metadata={
            "width": 1920,
            "height": 1080,
            "multi_touch": True,
            "max_touch_points": 10,
        }
    )
    
    # Connect to the touchscreen
    await touchscreen.connect()
    
    # Perform a tap
    await touchscreen.tap(500, 300)
    
    # Perform a double tap
    await touchscreen.double_tap(600, 400)
    
    # Perform a swipe
    await touchscreen.swipe(200, 500, 800, 500, duration=0.5)
    
    # Perform a pinch (zoom out)
    await touchscreen.pinch(
        center_x=960,
        center_y=540,
        start_distance=200,
        end_distance=100,
        duration=0.5
    )
    
    # Perform a pinch (zoom in)
    await touchscreen.pinch(
        center_x=960,
        center_y=540,
        start_distance=100,
        end_distance=200,
        duration=0.5
    )
    
    # Perform a rotation
    await touchscreen.rotate(
        center_x=960,
        center_y=540,
        radius=100,
        start_angle=0,
        end_angle=90,
        duration=0.5
    )
    
    # Disconnect from the touchscreen
    await touchscreen.disconnect()


async def gamepad_example():
    """Demonstrate gamepad device functionality."""
    logger.info("=== Gamepad Device Example ===")
    
    # Create a gamepad device
    gamepad = GamepadDevice(
        device_id="gamepad_01",
        name="Virtual Gamepad",
        metadata={
            "controller_type": "xbox",
            "battery_level": 0.75,
        }
    )
    
    # Connect to the gamepad
    await gamepad.connect()
    
    # Press some buttons
    await gamepad.press_button("a")
    await gamepad.press_button("b")
    await gamepad.press_button("x")
    await gamepad.press_button("y")
    
    # Press and hold a button
    await gamepad.button_down("right_bumper")
    await asyncio.sleep(0.5)
    await gamepad.button_up("right_bumper")
    
    # Set trigger values
    await gamepad.set_trigger("left_trigger", 0.5)
    await gamepad.set_trigger("right_trigger", 0.8)
    
    # Move analog sticks
    await gamepad.move_stick("left_stick", 0.5, 0.0)  # Move right
    await gamepad.move_stick("right_stick", 0.0, -0.7)  # Move up
    
    # Set vibration/rumble
    await gamepad.set_vibration(left_motor=0.7, right_motor=0.3)
    await asyncio.sleep(1.0)
    
    # Get current gamepad state
    state = await gamepad.get_state()
    logger.info(f"Gamepad state: {state}")
    
    # Reset gamepad state
    await gamepad.reset_state()
    
    # Disconnect from the gamepad
    await gamepad.disconnect()


async def execute_command_example():
    """Demonstrate using execute_command for input devices."""
    logger.info("=== Execute Command Example ===")
    
    # Create devices
    mouse = MouseDevice(device_id="mouse_01", name="Virtual Mouse")
    keyboard = KeyboardDevice(device_id="keyboard_01", name="Virtual Keyboard")
    
    # Connect to devices
    await mouse.connect()
    await keyboard.connect()
    
    # Execute commands on mouse
    await mouse.execute_command("move_to", {"x": 500, "y": 300})
    await mouse.execute_command("click", {"button": "left"})
    
    # Execute commands on keyboard
    await keyboard.execute_command("type_text", {"text": "Hello from execute_command!"})
    await keyboard.execute_command("press_hotkey", {"keys": ["ctrl", "s"]})
    
    # Disconnect from devices
    await mouse.disconnect()
    await keyboard.disconnect()


async def main():
    """Run all examples."""
    try:
        # Run mouse example
        await mouse_example()
        print()
        
        # Run keyboard example
        await keyboard_example()
        print()
        
        # Run touchscreen example
        await touchscreen_example()
        print()
        
        # Run gamepad example
        await gamepad_example()
        print()
        
        # Run execute_command example
        await execute_command_example()
        
    except Exception as e:
        logger.error(f"Error in example: {e}")


if __name__ == "__main__":
    asyncio.run(main())
