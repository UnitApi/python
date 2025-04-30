"""
Touchscreen device implementation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple, List

from .base import InputDevice, DeviceStatus


class TouchscreenDevice(InputDevice):
    """
    Touchscreen device implementation.
    """

    def __init__(
        self, device_id: str, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize touchscreen device.

        Args:
            device_id: Unique device identifier
            name: Device name
            metadata: Additional device information
        """
        super().__init__(
            device_id=device_id, name=name, device_type="touchscreen", metadata=metadata
        )
        self.logger = logging.getLogger(__name__)

        # Touchscreen-specific attributes
        self.width = metadata.get("width", 1920) if metadata else 1920
        self.height = metadata.get("height", 1080) if metadata else 1080
        self.multi_touch = metadata.get("multi_touch", True) if metadata else True
        self.max_touch_points = metadata.get("max_touch_points", 10) if metadata else 10

        # Current touch points
        self.active_touches: Dict[int, Dict[str, Any]] = {}  # touch_id -> touch data

    async def touch_down(self, x: int, y: int, touch_id: int = 0) -> Dict[str, Any]:
        """
        Begin a touch at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            touch_id: Touch identifier for multi-touch

        Returns:
            Touch operation result
        """
        try:
            if not self.multi_touch and len(self.active_touches) > 0:
                self.logger.warning(
                    "Multi-touch not supported, ignoring additional touch"
                )
                return {"error": "Multi-touch not supported"}

            if len(self.active_touches) >= self.max_touch_points:
                self.logger.warning(
                    f"Maximum touch points ({self.max_touch_points}) reached"
                )
                return {
                    "error": f"Maximum touch points ({self.max_touch_points}) reached"
                }

            self.logger.info(f"Touch down at ({x}, {y}) with ID {touch_id}")

            # Validate coordinates
            x = max(0, min(x, self.width))
            y = max(0, min(y, self.height))

            # Record touch
            self.active_touches[touch_id] = {
                "x": x,
                "y": y,
                "start_x": x,
                "start_y": y,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # Simulate touch
            await asyncio.sleep(0.05)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "position": (x, y),
                "state": "down",
            }
        except Exception as e:
            self.logger.error(f"Touch down failed: {e}")
            return {"error": str(e)}

    async def touch_move(self, x: int, y: int, touch_id: int = 0) -> Dict[str, Any]:
        """
        Move an active touch to the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            touch_id: Touch identifier for multi-touch

        Returns:
            Touch operation result
        """
        try:
            if touch_id not in self.active_touches:
                self.logger.warning(f"Touch ID {touch_id} not active")
                return {"error": f"Touch ID {touch_id} not active"}

            self.logger.info(f"Touch move to ({x}, {y}) with ID {touch_id}")

            # Validate coordinates
            x = max(0, min(x, self.width))
            y = max(0, min(y, self.height))

            # Update touch position
            self.active_touches[touch_id]["x"] = x
            self.active_touches[touch_id]["y"] = y

            # Simulate touch movement
            await asyncio.sleep(0.05)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "position": (x, y),
                "state": "move",
            }
        except Exception as e:
            self.logger.error(f"Touch move failed: {e}")
            return {"error": str(e)}

    async def touch_up(self, touch_id: int = 0) -> Dict[str, Any]:
        """
        End an active touch.

        Args:
            touch_id: Touch identifier for multi-touch

        Returns:
            Touch operation result
        """
        try:
            if touch_id not in self.active_touches:
                self.logger.warning(f"Touch ID {touch_id} not active")
                return {"error": f"Touch ID {touch_id} not active"}

            touch_data = self.active_touches[touch_id]
            x, y = touch_data["x"], touch_data["y"]
            start_x, start_y = touch_data["start_x"], touch_data["start_y"]

            self.logger.info(f"Touch up at ({x}, {y}) with ID {touch_id}")

            # Remove touch
            del self.active_touches[touch_id]

            # Simulate touch release
            await asyncio.sleep(0.05)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "position": (x, y),
                "start_position": (start_x, start_y),
                "state": "up",
            }
        except Exception as e:
            self.logger.error(f"Touch up failed: {e}")
            return {"error": str(e)}

    async def tap(self, x: int, y: int, touch_id: int = 0) -> Dict[str, Any]:
        """
        Perform a tap at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            touch_id: Touch identifier for multi-touch

        Returns:
            Tap operation result
        """
        try:
            self.logger.info(f"Tapping at ({x}, {y}) with ID {touch_id}")

            # Simulate tap (touch down and up)
            await self.touch_down(x, y, touch_id)
            await asyncio.sleep(0.1)
            result = await self.touch_up(touch_id)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "position": (x, y),
                "action": "tap",
            }
        except Exception as e:
            self.logger.error(f"Tap failed: {e}")
            return {"error": str(e)}

    async def double_tap(self, x: int, y: int, touch_id: int = 0) -> Dict[str, Any]:
        """
        Perform a double tap at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            touch_id: Touch identifier for multi-touch

        Returns:
            Double tap operation result
        """
        try:
            self.logger.info(f"Double-tapping at ({x}, {y}) with ID {touch_id}")

            # Simulate double tap
            await self.tap(x, y, touch_id)
            await asyncio.sleep(0.15)
            await self.tap(x, y, touch_id)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "position": (x, y),
                "action": "double_tap",
            }
        except Exception as e:
            self.logger.error(f"Double tap failed: {e}")
            return {"error": str(e)}

    async def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        touch_id: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform a swipe from start to end coordinates.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in seconds
            touch_id: Touch identifier for multi-touch

        Returns:
            Swipe operation result
        """
        try:
            self.logger.info(
                f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y}) "
                f"over {duration}s with ID {touch_id}"
            )

            # Validate coordinates
            start_x = max(0, min(start_x, self.width))
            start_y = max(0, min(start_y, self.height))
            end_x = max(0, min(end_x, self.width))
            end_y = max(0, min(end_y, self.height))

            # Calculate number of steps based on duration
            steps = max(int(duration * 20), 2)  # At least 2 steps

            # Calculate step increments
            dx = (end_x - start_x) / (steps - 1)
            dy = (end_y - start_y) / (steps - 1)
            step_time = duration / steps

            # Start touch
            await self.touch_down(start_x, start_y, touch_id)

            # Move touch in steps
            for i in range(1, steps - 1):
                x = int(start_x + dx * i)
                y = int(start_y + dy * i)
                await self.touch_move(x, y, touch_id)
                await asyncio.sleep(step_time)

            # Move to final position
            await self.touch_move(end_x, end_y, touch_id)

            # End touch
            await self.touch_up(touch_id)

            return {
                "status": "success",
                "device_id": self.device_id,
                "touch_id": touch_id,
                "start_position": (start_x, start_y),
                "end_position": (end_x, end_y),
                "duration": duration,
                "action": "swipe",
            }
        except Exception as e:
            self.logger.error(f"Swipe failed: {e}")
            # Ensure touch is released in case of error
            if touch_id in self.active_touches:
                await self.touch_up(touch_id)
            return {"error": str(e)}

    async def pinch(
        self,
        center_x: int,
        center_y: int,
        start_distance: int,
        end_distance: int,
        duration: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Perform a pinch gesture (zoom in/out).

        Args:
            center_x: Center X coordinate of the pinch
            center_y: Center Y coordinate of the pinch
            start_distance: Starting distance between touch points
            end_distance: Ending distance between touch points
            duration: Pinch duration in seconds

        Returns:
            Pinch operation result
        """
        try:
            if not self.multi_touch:
                self.logger.warning("Multi-touch not supported, cannot perform pinch")
                return {"error": "Multi-touch not supported"}

            pinch_in = end_distance < start_distance
            action = "pinch in" if pinch_in else "pinch out"

            self.logger.info(
                f"{action.capitalize()} at ({center_x}, {center_y}) "
                f"from {start_distance}px to {end_distance}px over {duration}s"
            )

            # Calculate start and end positions for two touch points
            half_start = start_distance / 2
            half_end = end_distance / 2

            start_points = [
                (center_x - half_start, center_y),
                (center_x + half_start, center_y),
            ]

            end_points = [
                (center_x - half_end, center_y),
                (center_x + half_end, center_y),
            ]

            # Calculate number of steps based on duration
            steps = max(int(duration * 20), 2)  # At least 2 steps
            step_time = duration / steps

            # Start touches
            for i, (x, y) in enumerate(start_points):
                await self.touch_down(int(x), int(y), i)

            # Move touches in steps
            for step in range(1, steps - 1):
                progress = step / (steps - 1)
                for i in range(2):
                    x1, y1 = start_points[i]
                    x2, y2 = end_points[i]
                    x = int(x1 + (x2 - x1) * progress)
                    y = int(y1 + (y2 - y1) * progress)
                    await self.touch_move(x, y, i)
                await asyncio.sleep(step_time)

            # Move to final positions
            for i, (x, y) in enumerate(end_points):
                await self.touch_move(int(x), int(y), i)

            # End touches
            for i in range(2):
                await self.touch_up(i)

            return {
                "status": "success",
                "device_id": self.device_id,
                "center": (center_x, center_y),
                "start_distance": start_distance,
                "end_distance": end_distance,
                "duration": duration,
                "action": action,
            }
        except Exception as e:
            self.logger.error(f"Pinch failed: {e}")
            # Ensure all touches are released in case of error
            for i in range(2):
                if i in self.active_touches:
                    await self.touch_up(i)
            return {"error": str(e)}

    async def rotate(
        self,
        center_x: int,
        center_y: int,
        radius: int,
        start_angle: float,
        end_angle: float,
        duration: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Perform a rotation gesture.

        Args:
            center_x: Center X coordinate of the rotation
            center_y: Center Y coordinate of the rotation
            radius: Distance from center to touch point
            start_angle: Starting angle in degrees
            end_angle: Ending angle in degrees
            duration: Rotation duration in seconds

        Returns:
            Rotation operation result
        """
        try:
            if not self.multi_touch:
                self.logger.warning(
                    "Multi-touch not supported, cannot perform rotation"
                )
                return {"error": "Multi-touch not supported"}

            import math

            self.logger.info(
                f"Rotating at ({center_x}, {center_y}) with radius {radius}px "
                f"from {start_angle}° to {end_angle}° over {duration}s"
            )

            # Calculate number of steps based on duration
            steps = max(int(duration * 20), 2)  # At least 2 steps
            step_time = duration / steps

            # Convert angles to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)

            # Calculate start position
            start_x = center_x + int(radius * math.cos(start_rad))
            start_y = center_y + int(radius * math.sin(start_rad))

            # Start touch
            await self.touch_down(start_x, start_y, 0)

            # Move touch in steps along the arc
            for step in range(1, steps):
                progress = step / (steps - 1)
                angle_rad = start_rad + (end_rad - start_rad) * progress

                x = center_x + int(radius * math.cos(angle_rad))
                y = center_y + int(radius * math.sin(angle_rad))

                await self.touch_move(x, y, 0)
                await asyncio.sleep(step_time)

            # End touch
            await self.touch_up(0)

            return {
                "status": "success",
                "device_id": self.device_id,
                "center": (center_x, center_y),
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle,
                "duration": duration,
                "action": "rotate",
            }
        except Exception as e:
            self.logger.error(f"Rotation failed: {e}")
            # Ensure touch is released in case of error
            if 0 in self.active_touches:
                await self.touch_up(0)
            return {"error": str(e)}

    async def connect(self) -> bool:
        """
        Connect to the touchscreen device.

        Returns:
            Connection status
        """
        try:
            # Simulated connection logic
            await asyncio.sleep(0.5)
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Touchscreen {self.device_id} connected")
            return True
        except Exception as e:
            self.status = DeviceStatus.ERROR
            self.logger.error(f"Touchscreen connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """
        Disconnect from the touchscreen device.

        Returns:
            Disconnection status
        """
        try:
            # Release any active touches before disconnecting
            active_touch_ids = list(self.active_touches.keys())
            for touch_id in active_touch_ids:
                await self.touch_up(touch_id)

            # Simulated disconnection logic
            await asyncio.sleep(0.3)
            self.status = DeviceStatus.OFFLINE
            self.logger.info(f"Touchscreen {self.device_id} disconnected")
            return True
        except Exception as e:
            self.logger.error(f"Touchscreen disconnection failed: {e}")
            return False

    async def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on the touchscreen device.

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
            if command == "touch_down":
                x = params.get("x", 0)
                y = params.get("y", 0)
                touch_id = params.get("touch_id", 0)
                return await self.touch_down(x, y, touch_id)
            elif command == "touch_move":
                x = params.get("x", 0)
                y = params.get("y", 0)
                touch_id = params.get("touch_id", 0)
                return await self.touch_move(x, y, touch_id)
            elif command == "touch_up":
                touch_id = params.get("touch_id", 0)
                return await self.touch_up(touch_id)
            elif command == "tap":
                x = params.get("x", 0)
                y = params.get("y", 0)
                touch_id = params.get("touch_id", 0)
                return await self.tap(x, y, touch_id)
            elif command == "double_tap":
                x = params.get("x", 0)
                y = params.get("y", 0)
                touch_id = params.get("touch_id", 0)
                return await self.double_tap(x, y, touch_id)
            elif command == "swipe":
                start_x = params.get("start_x", 0)
                start_y = params.get("start_y", 0)
                end_x = params.get("end_x", 0)
                end_y = params.get("end_y", 0)
                duration = params.get("duration", 0.5)
                touch_id = params.get("touch_id", 0)
                return await self.swipe(
                    start_x, start_y, end_x, end_y, duration, touch_id
                )
            elif command == "pinch":
                center_x = params.get("center_x", 0)
                center_y = params.get("center_y", 0)
                start_distance = params.get("start_distance", 100)
                end_distance = params.get("end_distance", 50)
                duration = params.get("duration", 0.5)
                return await self.pinch(
                    center_x, center_y, start_distance, end_distance, duration
                )
            elif command == "rotate":
                center_x = params.get("center_x", 0)
                center_y = params.get("center_y", 0)
                radius = params.get("radius", 100)
                start_angle = params.get("start_angle", 0)
                end_angle = params.get("end_angle", 90)
                duration = params.get("duration", 0.5)
                return await self.rotate(
                    center_x, center_y, radius, start_angle, end_angle, duration
                )
            else:
                raise ValueError(f"Unsupported command: {command}")
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"error": str(e)}
