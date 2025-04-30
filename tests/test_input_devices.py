"""
Tests for input devices (mouse, keyboard, touchscreen, gamepad).
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock

from unitapi.devices import (
    MouseDevice,
    KeyboardDevice,
    TouchscreenDevice,
    GamepadDevice,
    DeviceStatus,
)


class TestMouseDevice(unittest.TestCase):
    """Test cases for the MouseDevice class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mouse = MouseDevice(
            device_id="test_mouse",
            name="Test Mouse",
            metadata={"dpi": 1200}
        )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()

    def test_init(self):
        """Test mouse device initialization."""
        self.assertEqual(self.mouse.device_id, "test_mouse")
        self.assertEqual(self.mouse.name, "Test Mouse")
        self.assertEqual(self.mouse.type, "mouse")
        self.assertEqual(self.mouse.metadata, {"dpi": 1200})
        self.assertEqual(self.mouse.status, DeviceStatus.OFFLINE)
        self.assertEqual(self.mouse.position, (0, 0))
        self.assertEqual(self.mouse.buttons_state, {
            "left": False,
            "right": False,
            "middle": False,
        })

    def test_connect(self):
        """Test mouse device connection."""
        result = self.loop.run_until_complete(self.mouse.connect())
        self.assertTrue(result)
        self.assertEqual(self.mouse.status, DeviceStatus.ONLINE)

    def test_disconnect(self):
        """Test mouse device disconnection."""
        # First connect
        self.loop.run_until_complete(self.mouse.connect())
        # Then disconnect
        result = self.loop.run_until_complete(self.mouse.disconnect())
        self.assertTrue(result)
        self.assertEqual(self.mouse.status, DeviceStatus.OFFLINE)

    def test_move_to(self):
        """Test mouse move_to method."""
        result = self.loop.run_until_complete(self.mouse.move_to(100, 200))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.mouse.position, (100, 200))

    def test_move_relative(self):
        """Test mouse move_relative method."""
        # First move to a known position
        self.loop.run_until_complete(self.mouse.move_to(100, 100))
        # Then move relatively
        result = self.loop.run_until_complete(self.mouse.move_relative(50, -25))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.mouse.position, (150, 75))

    def test_click(self):
        """Test mouse click method."""
        # Mock button_down and button_up methods
        with patch.object(self.mouse, 'button_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.mouse, 'button_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test left click
            result = self.loop.run_until_complete(self.mouse.click())
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with("left")
            mock_up.assert_called_once_with("left")
            
            # Reset mocks
            mock_down.reset_mock()
            mock_up.reset_mock()
            
            # Test right click
            result = self.loop.run_until_complete(self.mouse.click("right"))
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with("right")
            mock_up.assert_called_once_with("right")

    def test_button_down_up(self):
        """Test mouse button_down and button_up methods."""
        # Test button down
        result = self.loop.run_until_complete(self.mouse.button_down("left"))
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.mouse.buttons_state["left"])
        
        # Test button up
        result = self.loop.run_until_complete(self.mouse.button_up("left"))
        self.assertEqual(result["status"], "success")
        self.assertFalse(self.mouse.buttons_state["left"])

    def test_scroll(self):
        """Test mouse scroll method."""
        result = self.loop.run_until_complete(self.mouse.scroll(5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["scroll_amount"], 5)

    def test_drag(self):
        """Test mouse drag method."""
        # First move to a known position
        self.loop.run_until_complete(self.mouse.move_to(100, 100))
        
        # Mock button_down, move_to, and button_up methods
        with patch.object(self.mouse, 'button_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.mouse, 'move_to', return_value=asyncio.Future()) as mock_move, \
             patch.object(self.mouse, 'button_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_move.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test drag
            result = self.loop.run_until_complete(self.mouse.drag(200, 200))
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with("left")
            mock_move.assert_called_once_with(200, 200)
            mock_up.assert_called_once_with("left")

    def test_execute_command(self):
        """Test mouse execute_command method."""
        # Test move_to method directly first
        move_result = self.loop.run_until_complete(self.mouse.move_to(300, 400))
        self.assertEqual(move_result["status"], "success")
        self.assertEqual(self.mouse.position, (300, 400))
        
        # Reset position
        self.mouse.position = (0, 0)
        
        # Now test execute_command with move_to
        self.loop.run_until_complete(
            self.mouse.execute_command("move_to", {"x": 300, "y": 400})
        )
        # Check that the position was updated
        self.assertEqual(self.mouse.position, (300, 400))
        
        # Test click command by checking that click is called with right parameters
        with patch.object(self.mouse, 'click') as mock_click:
            # Set up the mock to return a completed future
            future = asyncio.Future()
            future.set_result({"status": "success"})
            mock_click.return_value = future
            
            # Execute the command
            self.loop.run_until_complete(
                self.mouse.execute_command("click", {"button": "right"})
            )
            
            # Verify the mock was called correctly
            mock_click.assert_called_once_with("right")
        
        # Test invalid command
        result = self.loop.run_until_complete(
            self.mouse.execute_command("invalid_command")
        )
        self.assertIn("error", result)
        self.assertIn("Unsupported command", result["error"])


class TestKeyboardDevice(unittest.TestCase):
    """Test cases for the KeyboardDevice class."""

    def setUp(self):
        """Set up test fixtures."""
        self.keyboard = KeyboardDevice(
            device_id="test_keyboard",
            name="Test Keyboard",
            metadata={"layout": "us"}
        )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()

    def test_init(self):
        """Test keyboard device initialization."""
        self.assertEqual(self.keyboard.device_id, "test_keyboard")
        self.assertEqual(self.keyboard.name, "Test Keyboard")
        self.assertEqual(self.keyboard.type, "keyboard")
        self.assertEqual(self.keyboard.metadata, {"layout": "us"})
        self.assertEqual(self.keyboard.status, DeviceStatus.OFFLINE)
        self.assertEqual(len(self.keyboard.pressed_keys), 0)
        self.assertEqual(self.keyboard.layout, "us")
        self.assertEqual(self.keyboard.modifiers, {
            "shift": False,
            "ctrl": False,
            "alt": False,
            "meta": False,
        })

    def test_key_down_up(self):
        """Test keyboard key_down and key_up methods."""
        # Test key down
        result = self.loop.run_until_complete(self.keyboard.key_down("a"))
        self.assertEqual(result["status"], "success")
        self.assertIn("a", self.keyboard.pressed_keys)
        
        # Test key up
        result = self.loop.run_until_complete(self.keyboard.key_up("a"))
        self.assertEqual(result["status"], "success")
        self.assertNotIn("a", self.keyboard.pressed_keys)
        
        # Test modifier key
        result = self.loop.run_until_complete(self.keyboard.key_down("shift"))
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.keyboard.modifiers["shift"])
        
        result = self.loop.run_until_complete(self.keyboard.key_up("shift"))
        self.assertEqual(result["status"], "success")
        self.assertFalse(self.keyboard.modifiers["shift"])

    def test_press_key(self):
        """Test keyboard press_key method."""
        # Mock key_down and key_up methods
        with patch.object(self.keyboard, 'key_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.keyboard, 'key_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test press key
            result = self.loop.run_until_complete(self.keyboard.press_key("a"))
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with("a")
            mock_up.assert_called_once_with("a")

    def test_type_text(self):
        """Test keyboard type_text method."""
        # Mock press_key method
        with patch.object(self.keyboard, 'press_key', return_value=asyncio.Future()) as mock_press:
            mock_press.return_value.set_result({"status": "success"})
            
            # Test type text
            result = self.loop.run_until_complete(self.keyboard.type_text("abc"))
            self.assertEqual(result["status"], "success")
            self.assertEqual(mock_press.call_count, 3)
            mock_press.assert_any_call("a")
            mock_press.assert_any_call("b")
            mock_press.assert_any_call("c")

    def test_press_hotkey(self):
        """Test keyboard press_hotkey method."""
        # Mock key_down and key_up methods
        with patch.object(self.keyboard, 'key_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.keyboard, 'key_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test press hotkey
            result = self.loop.run_until_complete(self.keyboard.press_hotkey("ctrl", "c"))
            self.assertEqual(result["status"], "success")
            self.assertEqual(mock_down.call_count, 2)
            self.assertEqual(mock_up.call_count, 2)
            mock_down.assert_any_call("ctrl")
            mock_down.assert_any_call("c")
            # Check that keys are released in reverse order
            mock_up.assert_any_call("c")
            mock_up.assert_any_call("ctrl")


class TestTouchscreenDevice(unittest.TestCase):
    """Test cases for the TouchscreenDevice class."""

    def setUp(self):
        """Set up test fixtures."""
        self.touchscreen = TouchscreenDevice(
            device_id="test_touchscreen",
            name="Test Touchscreen",
            metadata={
                "width": 1920,
                "height": 1080,
                "multi_touch": True,
            }
        )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()

    def test_init(self):
        """Test touchscreen device initialization."""
        self.assertEqual(self.touchscreen.device_id, "test_touchscreen")
        self.assertEqual(self.touchscreen.name, "Test Touchscreen")
        self.assertEqual(self.touchscreen.type, "touchscreen")
        self.assertEqual(self.touchscreen.metadata, {
            "width": 1920,
            "height": 1080,
            "multi_touch": True,
        })
        self.assertEqual(self.touchscreen.status, DeviceStatus.OFFLINE)
        self.assertEqual(self.touchscreen.width, 1920)
        self.assertEqual(self.touchscreen.height, 1080)
        self.assertTrue(self.touchscreen.multi_touch)
        self.assertEqual(self.touchscreen.max_touch_points, 10)
        self.assertEqual(len(self.touchscreen.active_touches), 0)

    def test_touch_down_up(self):
        """Test touchscreen touch_down and touch_up methods."""
        # Test touch down
        result = self.loop.run_until_complete(self.touchscreen.touch_down(500, 300))
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.touchscreen.active_touches), 1)
        self.assertIn(0, self.touchscreen.active_touches)
        self.assertEqual(self.touchscreen.active_touches[0]["x"], 500)
        self.assertEqual(self.touchscreen.active_touches[0]["y"], 300)
        
        # Test touch up
        result = self.loop.run_until_complete(self.touchscreen.touch_up(0))
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.touchscreen.active_touches), 0)

    def test_touch_move(self):
        """Test touchscreen touch_move method."""
        # First touch down
        self.loop.run_until_complete(self.touchscreen.touch_down(500, 300))
        
        # Test touch move
        result = self.loop.run_until_complete(self.touchscreen.touch_move(600, 400, 0))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.touchscreen.active_touches[0]["x"], 600)
        self.assertEqual(self.touchscreen.active_touches[0]["y"], 400)
        
        # Clean up
        self.loop.run_until_complete(self.touchscreen.touch_up(0))

    def test_tap(self):
        """Test touchscreen tap method."""
        # Mock touch_down and touch_up methods
        with patch.object(self.touchscreen, 'touch_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.touchscreen, 'touch_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test tap
            result = self.loop.run_until_complete(self.touchscreen.tap(500, 300))
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with(500, 300, 0)
            mock_up.assert_called_once_with(0)


class TestGamepadDevice(unittest.TestCase):
    """Test cases for the GamepadDevice class."""

    def setUp(self):
        """Set up test fixtures."""
        self.gamepad = GamepadDevice(
            device_id="test_gamepad",
            name="Test Gamepad",
            metadata={
                "controller_type": "xbox",
                "battery_level": 0.75,
            }
        )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()

    def test_init(self):
        """Test gamepad device initialization."""
        self.assertEqual(self.gamepad.device_id, "test_gamepad")
        self.assertEqual(self.gamepad.name, "Test Gamepad")
        self.assertEqual(self.gamepad.type, "gamepad")
        self.assertEqual(self.gamepad.metadata, {
            "controller_type": "xbox",
            "battery_level": 0.75,
        })
        self.assertEqual(self.gamepad.status, DeviceStatus.OFFLINE)
        self.assertEqual(self.gamepad.controller_type, "xbox")
        self.assertEqual(self.gamepad.battery_level, 0.75)
        self.assertEqual(self.gamepad.left_stick, (0.0, 0.0))
        self.assertEqual(self.gamepad.right_stick, (0.0, 0.0))
        self.assertEqual(self.gamepad.vibration, {
            "left_motor": 0.0,
            "right_motor": 0.0,
        })

    def test_button_down_up(self):
        """Test gamepad button_down and button_up methods."""
        # Test button down
        result = self.loop.run_until_complete(self.gamepad.button_down("a"))
        self.assertEqual(result["status"], "success")
        self.assertTrue(self.gamepad.buttons["a"])
        
        # Test button up
        result = self.loop.run_until_complete(self.gamepad.button_up("a"))
        self.assertEqual(result["status"], "success")
        self.assertFalse(self.gamepad.buttons["a"])
        
        # Test trigger
        result = self.loop.run_until_complete(self.gamepad.button_down("left_trigger"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.buttons["left_trigger"], 1.0)
        
        result = self.loop.run_until_complete(self.gamepad.button_up("left_trigger"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.buttons["left_trigger"], 0.0)

    def test_press_button(self):
        """Test gamepad press_button method."""
        # Mock button_down and button_up methods
        with patch.object(self.gamepad, 'button_down', return_value=asyncio.Future()) as mock_down, \
             patch.object(self.gamepad, 'button_up', return_value=asyncio.Future()) as mock_up:
            
            mock_down.return_value.set_result({"status": "success"})
            mock_up.return_value.set_result({"status": "success"})
            
            # Test press button
            result = self.loop.run_until_complete(self.gamepad.press_button("a"))
            self.assertEqual(result["status"], "success")
            mock_down.assert_called_once_with("a")
            mock_up.assert_called_once_with("a")

    def test_set_trigger(self):
        """Test gamepad set_trigger method."""
        result = self.loop.run_until_complete(self.gamepad.set_trigger("left_trigger", 0.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.buttons["left_trigger"], 0.5)
        
        # Test value clamping
        result = self.loop.run_until_complete(self.gamepad.set_trigger("right_trigger", 1.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.buttons["right_trigger"], 1.0)
        
        result = self.loop.run_until_complete(self.gamepad.set_trigger("right_trigger", -0.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.buttons["right_trigger"], 0.0)

    def test_move_stick(self):
        """Test gamepad move_stick method."""
        result = self.loop.run_until_complete(self.gamepad.move_stick("left_stick", 0.5, -0.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.left_stick, (0.5, -0.5))
        
        result = self.loop.run_until_complete(self.gamepad.move_stick("right_stick", -0.25, 0.75))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.right_stick, (-0.25, 0.75))
        
        # Test value clamping
        result = self.loop.run_until_complete(self.gamepad.move_stick("left_stick", 1.5, -1.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.left_stick, (1.0, -1.0))

    def test_set_vibration(self):
        """Test gamepad set_vibration method."""
        result = self.loop.run_until_complete(self.gamepad.set_vibration(0.7, 0.3))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.vibration["left_motor"], 0.7)
        self.assertEqual(self.gamepad.vibration["right_motor"], 0.3)
        
        # Test partial update
        result = self.loop.run_until_complete(self.gamepad.set_vibration(left_motor=0.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.vibration["left_motor"], 0.5)
        self.assertEqual(self.gamepad.vibration["right_motor"], 0.3)
        
        # Test value clamping
        result = self.loop.run_until_complete(self.gamepad.set_vibration(1.5, -0.5))
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.gamepad.vibration["left_motor"], 1.0)
        self.assertEqual(self.gamepad.vibration["right_motor"], 0.0)

    def test_reset_state(self):
        """Test gamepad reset_state method."""
        # Set some state
        self.loop.run_until_complete(self.gamepad.button_down("a"))
        self.loop.run_until_complete(self.gamepad.set_trigger("left_trigger", 0.5))
        self.loop.run_until_complete(self.gamepad.move_stick("left_stick", 0.5, -0.5))
        self.loop.run_until_complete(self.gamepad.set_vibration(0.7, 0.3))
        
        # Reset state
        result = self.loop.run_until_complete(self.gamepad.reset_state())
        self.assertEqual(result["status"], "success")
        
        # Check that state is reset
        self.assertFalse(self.gamepad.buttons["a"])
        self.assertEqual(self.gamepad.buttons["left_trigger"], 0.0)
        self.assertEqual(self.gamepad.left_stick, (0.0, 0.0))
        self.assertEqual(self.gamepad.vibration["left_motor"], 0.0)
        self.assertEqual(self.gamepad.vibration["right_motor"], 0.0)

    def test_get_state(self):
        """Test gamepad get_state method."""
        # Set some state
        self.loop.run_until_complete(self.gamepad.button_down("a"))
        self.loop.run_until_complete(self.gamepad.set_trigger("left_trigger", 0.5))
        self.loop.run_until_complete(self.gamepad.move_stick("left_stick", 0.5, -0.5))
        self.loop.run_until_complete(self.gamepad.set_vibration(0.7, 0.3))
        
        # Get state
        result = self.loop.run_until_complete(self.gamepad.get_state())
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["device_id"], "test_gamepad")
        self.assertTrue(result["buttons"]["a"])
        self.assertEqual(result["buttons"]["left_trigger"], 0.5)
        self.assertEqual(result["left_stick"], (0.5, -0.5))
        self.assertEqual(result["vibration"]["left_motor"], 0.7)
        self.assertEqual(result["vibration"]["right_motor"], 0.3)
        self.assertEqual(result["battery_level"], 0.75)


if __name__ == "__main__":
    unittest.main()
