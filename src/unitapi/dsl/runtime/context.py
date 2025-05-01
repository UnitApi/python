from typing import Dict, Any, List, Optional, Callable
import logging
import asyncio

logger = logging.getLogger(__name__)


class DSLContext:
    """
    Execution context for DSL configurations

    This class provides a context for executing DSL configurations, including
    variables, state management, and event handling.
    """

    def __init__(self):
        """Initialize the DSL context"""
        self.variables = {}
        self.state = {}
        self.event_handlers = {}
        self.tasks = []

    def set_variable(self, name: str, value: Any):
        """
        Set a variable in the context

        Args:
            name: Variable name
            value: Variable value
        """
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable from the context

        Args:
            name: Variable name
            default: Default value if variable doesn't exist

        Returns:
            The variable value or default
        """
        return self.variables.get(name, default)

    def set_state(self, key: str, value: Any):
        """
        Set state value

        Args:
            key: State key
            value: State value
        """
        old_value = self.state.get(key)
        self.state[key] = value

        # Trigger state change event
        if old_value != value:
            self.trigger_event(
                f"state_changed:{key}",
                {"key": key, "old_value": old_value, "new_value": value},
            )

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get state value

        Args:
            key: State key
            default: Default value if state doesn't exist

        Returns:
            The state value or default
        """
        return self.state.get(key, default)

    def register_event_handler(self, event_name: str, handler: Callable):
        """
        Register an event handler

        Args:
            event_name: Event name
            handler: Event handler function
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

        self.event_handlers[event_name].append(handler)

    def unregister_event_handler(self, event_name: str, handler: Callable) -> bool:
        """
        Unregister an event handler

        Args:
            event_name: Event name
            handler: Event handler function

        Returns:
            True if handler was removed, False otherwise
        """
        if event_name not in self.event_handlers:
            return False

        if handler in self.event_handlers[event_name]:
            self.event_handlers[event_name].remove(handler)
            return True

        return False

    async def trigger_event(self, event_name: str, event_data: Dict[str, Any] = None):
        """
        Trigger an event

        Args:
            event_name: Event name
            event_data: Event data
        """
        if event_data is None:
            event_data = {}

        logger.debug(f"Event triggered: {event_name} with data: {event_data}")

        # Call handlers for this specific event
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_name, event_data)
                    else:
                        handler(event_name, event_data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_name}: {e}")

        # Call handlers for wildcard events
        if "*" in self.event_handlers:
            for handler in self.event_handlers["*"]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_name, event_data)
                    else:
                        handler(event_name, event_data)
                except Exception as e:
                    logger.error(
                        f"Error in wildcard event handler for {event_name}: {e}"
                    )

    def create_task(self, coro):
        """
        Create a background task

        Args:
            coro: Coroutine to run as a task

        Returns:
            The created task
        """
        task = asyncio.create_task(coro)
        self.tasks.append(task)

        # Remove task from list when done
        task.add_done_callback(
            lambda t: self.tasks.remove(t) if t in self.tasks else None
        )

        return task

    async def cancel_all_tasks(self):
        """Cancel all background tasks"""
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self.tasks = []

    def clear(self):
        """Clear all context data"""
        self.variables = {}
        self.state = {}
        self.event_handlers = {}

    async def cleanup(self):
        """Clean up resources"""
        await self.cancel_all_tasks()
        self.clear()
