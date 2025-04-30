"""
access_control.py
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum, auto


class AccessLevel(Enum):
    """
    Predefined access levels for device and system interactions.
    """
    NONE = auto()  # No access
    READ = auto()  # Read-only access
    WRITE = auto()  # Modify device state
    ADMIN = auto()  # Full system control


class AccessControlManager:
    """
    Comprehensive access control and permission management.
    """

    def __init__(self):
        """
        Initialize access control system.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Role-based access control mappings
        self._role_permissions: Dict[str, Dict[str, AccessLevel]] = {
            'admin': {
                'devices': AccessLevel.ADMIN,
                'system': AccessLevel.ADMIN,
                'network': AccessLevel.ADMIN
            },
            'operator': {
                'devices': AccessLevel.WRITE,
                'system': AccessLevel.READ,
                'network': AccessLevel.READ
            },
            'viewer': {
                'devices': AccessLevel.READ,
                'system': AccessLevel.READ,
                'network': AccessLevel.NONE
            }
        }

        # Resource-specific access rules
        self._resource_access: Dict[str, Dict[str, List[str]]] = {
            'temperature_sensor': {
                'read': ['admin', 'operator', 'viewer'],
                'write': ['admin', 'operator']
            },
            'camera': {
                'read': ['admin', 'operator', 'viewer'],
                'control': ['admin', 'operator']
            }
        }

        # Dynamic rule registry
        self._dynamic_rules: List[Callable] = []

    def define_role(
            self,
            role_name: str,
            permissions: Dict[str, AccessLevel]
    ) -> None:
        """
        Define or modify a role's permissions.

        :param role_name: Name of the role
        :param permissions: Permission mappings
        """
        self._role_permissions[role_name] = permissions
        self.logger.info(f"Defined role: {role_name}")

    def add_resource_rule(
            self,
            resource: str,
            action: str,
            allowed_roles: List[str]
    ) -> None:
        """
        Add a resource-specific access rule.

        :param resource: Resource identifier
        :param action: Action type (read, write, control)
        :param allowed_roles: Roles allowed to perform the action
        """
        if resource not in self._resource_access:
            self._resource_access[resource] = {}

        self._resource_access[resource][action] = allowed_roles
        self.logger.info(f"Added rule for {resource}: {action}")

    def add_dynamic_rule(self, rule_func: Callable) -> None:
        """
        Add a dynamic access control rule.

        :param rule_func: Function to evaluate dynamic access
        """
        self._dynamic_rules.append(rule_func)
        self.logger.info("Added dynamic access rule")

    def check_access(
            self,
            role: str,
            resource: str,
            action: str,
            context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a role has access to perform an action on a resource.

        :param role: User role
        :param resource: Resource identifier
        :param action: Action to perform
        :param context: Additional context for dynamic rules
        :return: Access granted status
        """
        # Role existence check
        if role not in self._role_permissions:
            self.logger.warning(f"Unknown role: {role}")
            return False

        # Resource-specific rule check
        if resource in self._resource_access:
            resource_rules = self._resource_access[resource]
            if action in resource_rules:
                if role not in resource_rules[action]:
                    self.logger.warning(
                        f"Role {role} not allowed to {action} on {resource}"
                    )
                    return False

        # Dynamic rule evaluation
        for rule in self._dynamic_rules:
            try:
                if not rule(role, resource, action, context):
                    self.logger.warning(
                        f"Dynamic rule denied access for {role} on {resource}"
                    )
                    return False
            except Exception as e:
                self.logger.error(f"Dynamic rule error: {e}")
                return False

        return True

    async def audit_access(
            self,
            role: str,
            resource: str,
            action: str,
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive access audit with detailed logging.

        :param role: User role
        :param resource: Resource identifier
        :param action: Action to perform
        :param context: Additional context for audit
        :return: Audit result
        """
        access_granted = self.check_access(role, resource, action, context)

        audit_log = {
            'timestamp': asyncio.get_event_loop().time(),
            'role': role,
            'resource': resource,
            'action': action,
            'access_granted': access_granted,
            'context': context or {}
        }

        # Optional: Persist audit log (could be extended to database)
        await self._log_audit(audit_log)

        return audit_log

    async def _log_audit(self, audit_entry: Dict[str, Any]) -> None:
        """
        Log access audit entry.

        :param audit_entry: Audit log details
        """
        # Simulated logging - could be replaced with database or file logging
        self.logger.info(f"Access Audit: {audit_entry}")


# Example usage
async def main():
    """
    Demonstrate access control manager functionality.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create access control manager
    acl_manager = AccessControlManager()

    # Define custom dynamic rule
    def temperature_limit_rule(
            role: str,
            resource: str,
            action: str,
            context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Example dynamic rule: Prevent temperature changes beyond safe limits.
        """
        if resource == 'temperature_sensor' and action == 'write':
            # Example: Only allow temperature changes within 18-30°C range
            if context and context.get('temperature'):
                temp = context['temperature']
                return 18 <= temp <= 30
        return True

    # Add dynamic rule
    acl_manager.add_dynamic_rule(temperature_limit_rule)

    # Test access scenarios
    print("Admin access to sensor:")
    admin_result = await acl_manager.audit_access(
        role='admin',
        resource='temperature_sensor',
        action='write',
        context={'temperature': 22}
    )
    print(admin_result)

    print("\nOperator access to sensor:")
    operator_result = await acl_manager.audit_access(
        role='operator',
        resource='temperature_sensor',
        action='write',
        context={'temperature': 35}
    )
    print(operator_result)

    print("\nViewer access to sensor:")
    viewer_result = await acl_manager.audit_access(
        role='viewer',
        resource='temperature_sensor',
        action='write'
    )
    print(viewer_result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())