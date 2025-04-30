# UnitAPI Security

UnitAPI provides comprehensive security features to protect device communications and ensure proper access control. This document outlines the security mechanisms available in UnitAPI and best practices for securing your applications.

## Overview

Security is a critical aspect of any IoT or device management system. UnitAPI implements several security layers to protect against unauthorized access, data breaches, and other security threats.

## Authentication

UnitAPI provides a flexible authentication system that supports various authentication methods.

### Token-based Authentication

```python
from unitapi.security.authentication import AuthenticationManager
import asyncio

async def main():
    # Create authentication manager
    auth_manager = AuthenticationManager()
    
    # Register a user
    await auth_manager.register_user(
        username='admin', 
        password='secure_password', 
        roles=['admin', 'user']
    )
    
    # Authenticate and get token
    token = await auth_manager.authenticate('admin', 'secure_password')
    print(f"Authentication token: {token}")
    
    # Verify token
    is_valid = await auth_manager.verify_token(token)
    print(f"Token is valid: {is_valid}")
    
    # Get user information from token
    user_info = await auth_manager.get_user_from_token(token)
    print(f"User info: {user_info}")

asyncio.run(main())
```

### Integrating Authentication with Server

```python
from unitapi.core.server import UnitAPIServer
from unitapi.security.authentication import AuthenticationManager
import asyncio

async def main():
    # Create server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create authentication manager
    auth_manager = AuthenticationManager()
    
    # Register users
    await auth_manager.register_user('admin', 'admin_password', ['admin'])
    await auth_manager.register_user('user', 'user_password', ['user'])
    
    # Set authentication manager for server
    server.set_authentication_manager(auth_manager)
    
    # Start server
    await server.start()

asyncio.run(main())
```

### Client Authentication

```python
from unitapi.core.client import UnitAPIClient
import asyncio

async def main():
    # Create client
    client = UnitAPIClient(server_host='localhost', server_port=7890)
    
    # Authenticate
    token = await client.authenticate('admin', 'admin_password')
    
    # Use token for subsequent requests
    client.set_auth_token(token)
    
    # List devices (authenticated request)
    devices = await client.list_devices()
    print(f"Devices: {devices}")

asyncio.run(main())
```

## Access Control

UnitAPI implements a role-based access control system that allows fine-grained control over device operations.

### Access Control Manager

```python
from unitapi.security.access_control import AccessControlManager
import asyncio

async def main():
    # Create access control manager
    acl_manager = AccessControlManager()
    
    # Define static rules
    acl_manager.add_rule('admin', 'device:*', 'read:*')
    acl_manager.add_rule('admin', 'device:*', 'write:*')
    acl_manager.add_rule('user', 'device:sensor', 'read:*')
    acl_manager.add_rule('user', 'device:camera', 'read:image')
    
    # Check access
    admin_can_write = acl_manager.check_access('admin', 'device:camera', 'write:config')
    user_can_read = acl_manager.check_access('user', 'device:sensor', 'read:temperature')
    user_cannot_write = not acl_manager.check_access('user', 'device:camera', 'write:config')
    
    print(f"Admin can write camera config: {admin_can_write}")
    print(f"User can read sensor temperature: {user_can_read}")
    print(f"User cannot write camera config: {user_cannot_write}")
    
    # Define dynamic rule
    def temperature_limit_rule(role, resource, action, context):
        if resource == 'device:thermostat' and action == 'write:temperature':
            # Prevent temperature changes beyond safe limits
            temp = context.get('temperature', 0)
            return 18 <= temp <= 30
        return True
    
    # Add dynamic rule
    acl_manager.add_dynamic_rule(temperature_limit_rule)
    
    # Check dynamic rule
    safe_temp = acl_manager.check_access(
        'user', 'device:thermostat', 'write:temperature',
        context={'temperature': 22}
    )
    
    unsafe_temp = not acl_manager.check_access(
        'user', 'device:thermostat', 'write:temperature',
        context={'temperature': 35}
    )
    
    print(f"User can set safe temperature: {safe_temp}")
    print(f"User cannot set unsafe temperature: {unsafe_temp}")

asyncio.run(main())
```

### Integrating Access Control with Server

```python
from unitapi.core.server import UnitAPIServer
from unitapi.security.authentication import AuthenticationManager
from unitapi.security.access_control import AccessControlManager
import asyncio

async def main():
    # Create server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create authentication manager
    auth_manager = AuthenticationManager()
    
    # Register users
    await auth_manager.register_user('admin', 'admin_password', ['admin'])
    await auth_manager.register_user('user', 'user_password', ['user'])
    
    # Create access control manager
    acl_manager = AccessControlManager()
    
    # Define access rules
    acl_manager.add_rule('admin', 'device:*', '*')
    acl_manager.add_rule('user', 'device:sensor', 'read:*')
    
    # Set security managers for server
    server.set_authentication_manager(auth_manager)
    server.set_access_control_manager(acl_manager)
    
    # Start server
    await server.start()

asyncio.run(main())
```

## Encryption

UnitAPI provides encryption utilities to secure sensitive data.

### Data Encryption

```python
from unitapi.security.encryption import EncryptionManager
import asyncio

async def main():
    # Create encryption manager
    encryption_manager = EncryptionManager()
    
    # Generate encryption key
    key = encryption_manager.generate_key()
    
    # Encrypt data
    sensitive_data = "This is sensitive information"
    encrypted_data = encryption_manager.encrypt(sensitive_data, key)
    print(f"Encrypted data: {encrypted_data}")
    
    # Decrypt data
    decrypted_data = encryption_manager.decrypt(encrypted_data, key)
    print(f"Decrypted data: {decrypted_data}")
    
    # Secure hash
    password = "user_password"
    hashed_password = encryption_manager.hash_password(password)
    print(f"Hashed password: {hashed_password}")
    
    # Verify password
    is_valid = encryption_manager.verify_password(password, hashed_password)
    print(f"Password is valid: {is_valid}")

asyncio.run(main())
```

### Secure Communication

```python
from unitapi.protocols.websocket import WebSocketProtocol
from unitapi.security.encryption import EncryptionManager
import asyncio
import json

# Create encryption manager
encryption_manager = EncryptionManager()
key = encryption_manager.generate_key()

async def main():
    # Create WebSocket protocol handler
    ws_client = WebSocketProtocol(host='localhost', port=8765)
    
    # Connect to WebSocket server
    await ws_client.connect()
    
    # Define a secure message handler
    async def handle_encrypted_data(data):
        # Decrypt the received data
        encrypted_payload = data.get('payload')
        decrypted_payload = encryption_manager.decrypt(encrypted_payload, key)
        payload = json.loads(decrypted_payload)
        print(f"Received decrypted data: {payload}")
    
    # Register the message handler
    ws_client.add_message_handler('encrypted_data', handle_encrypted_data)
    
    # Send an encrypted message
    payload = {
        'device_id': 'sensor_01',
        'command': 'read_temperature',
        'timestamp': asyncio.get_event_loop().time()
    }
    
    # Encrypt the payload
    encrypted_payload = encryption_manager.encrypt(json.dumps(payload), key)
    
    # Send the encrypted message
    await ws_client.send('encrypted_data', {
        'payload': encrypted_payload
    })
    
    # Wait for some time to receive messages
    await asyncio.sleep(10)
    
    # Disconnect when done
    await ws_client.disconnect()

asyncio.run(main())
```

## Audit Logging

UnitAPI includes audit logging capabilities to track security-related events.

```python
from unitapi.security.authentication import AuthenticationManager
from unitapi.security.access_control import AccessControlManager
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='unitapi_audit.log'
)

async def main():
    # Create authentication manager with audit logging
    auth_manager = AuthenticationManager(enable_audit=True)
    
    # Register a user
    await auth_manager.register_user('admin', 'admin_password', ['admin'])
    
    # Authenticate (this will generate an audit log entry)
    token = await auth_manager.authenticate('admin', 'admin_password')
    
    # Failed authentication attempt (this will generate an audit log entry)
    try:
        await auth_manager.authenticate('admin', 'wrong_password')
    except Exception:
        pass
    
    # Create access control manager with audit logging
    acl_manager = AccessControlManager(enable_audit=True)
    
    # Define access rules
    acl_manager.add_rule('admin', 'device:camera', 'read:image')
    
    # Check access (this will generate an audit log entry)
    acl_manager.check_access('admin', 'device:camera', 'read:image')
    
    # Denied access attempt (this will generate an audit log entry)
    acl_manager.check_access('user', 'device:camera', 'write:config')

asyncio.run(main())
```

## Security Best Practices

### 1. Authentication and Authorization

- Always use authentication for production deployments
- Implement role-based access control
- Use strong passwords and consider password policies
- Regularly rotate authentication tokens

### 2. Secure Communication

- Use encrypted protocols (WSS instead of WS, MQTTS instead of MQTT)
- Encrypt sensitive data before transmission
- Validate and sanitize all input data
- Implement TLS/SSL for all network communications

### 3. Device Security

- Secure device credentials
- Implement device authentication
- Regularly update device firmware
- Monitor device behavior for anomalies

### 4. Audit and Monitoring

- Enable audit logging
- Regularly review audit logs
- Set up alerts for suspicious activities
- Implement monitoring for security events

### 5. Secure Deployment

- Follow the principle of least privilege
- Secure the server environment
- Keep dependencies updated
- Regularly perform security assessments

## Secure Configuration Example

Here's a comprehensive example of a secure UnitAPI configuration:

```python
from unitapi.core.server import UnitAPIServer
from unitapi.security.authentication import AuthenticationManager
from unitapi.security.access_control import AccessControlManager
from unitapi.security.encryption import EncryptionManager
from unitapi.protocols.websocket import WebSocketProtocol
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='unitapi_secure.log'
)

async def main():
    # Create server
    server = UnitAPIServer(host='0.0.0.0', port=7890)
    
    # Create authentication manager
    auth_manager = AuthenticationManager(enable_audit=True)
    
    # Register users
    await auth_manager.register_user('admin', 'strong_admin_password', ['admin'])
    await auth_manager.register_user('operator', 'strong_operator_password', ['operator'])
    await auth_manager.register_user('viewer', 'strong_viewer_password', ['viewer'])
    
    # Create access control manager
    acl_manager = AccessControlManager(enable_audit=True)
    
    # Define access rules
    # Admin can do everything
    acl_manager.add_rule('admin', 'device:*', '*')
    
    # Operator can read all devices and control some
    acl_manager.add_rule('operator', 'device:*', 'read:*')
    acl_manager.add_rule('operator', 'device:sensor', 'write:config')
    acl_manager.add_rule('operator', 'device:camera', 'write:config')
    
    # Viewer can only read
    acl_manager.add_rule('viewer', 'device:*', 'read:*')
    
    # Create encryption manager
    encryption_manager = EncryptionManager()
    
    # Set security managers for server
    server.set_authentication_manager(auth_manager)
    server.set_access_control_manager(acl_manager)
    server.set_encryption_manager(encryption_manager)
    
    # Create secure WebSocket protocol
    # In production, use wss:// instead of ws://
    websocket = WebSocketProtocol(host='0.0.0.0', port=8765)
    
    # Start the server and protocols
    server_task = asyncio.create_task(server.start())
    websocket_task = asyncio.create_task(websocket.create_server())
    
    # Wait for all tasks
    await asyncio.gather(server_task, websocket_task)

asyncio.run(main())
```

## Conclusion

Security is a critical aspect of any device management system. UnitAPI provides comprehensive security features to protect your devices and data. By following the best practices outlined in this document, you can ensure that your UnitAPI applications are secure and resilient against security threats.
