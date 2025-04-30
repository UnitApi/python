"""
authentication.py
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class AuthenticationManager:
    """
    Authentication and authorization management for UnitAPI.
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize authentication manager.

        :param secret_key: Secret key for token generation
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._users: Dict[str, Dict[str, Any]] = {}
        self._active_tokens: Dict[str, Dict[str, Any]] = {}

        # Use Python-jose for token generation if available
        try:
            import jose
            self._jwt_available = True
        except ImportError:
            self.logger.warning("python-jose not installed. Token features limited.")
            self._jwt_available = False

        # Secret key for token generation
        self._secret_key = secret_key or self._generate_secret_key()

    def _generate_secret_key(self) -> str:
        """
        Generate a random secret key.

        :return: Generated secret key
        """
        import secrets
        return secrets.token_hex(32)

    async def register_user(
            self,
            username: str,
            password: str,
            roles: Optional[list] = None
    ) -> bool:
        """
        Register a new user.

        :param username: User's username
        :param password: User's password
        :param roles: User roles
        :return: Registration status
        """
        # Hash password securely
        hashed_password = await self._hash_password(password)

        if username in self._users:
            self.logger.warning(f"User {username} already exists")
            return False

        self._users[username] = {
            'password': hashed_password,
            'roles': roles or ['user'],
            'created_at': datetime.now()
        }

        self.logger.info(f"User {username} registered successfully")
        return True

    async def authenticate(
            self,
            username: str,
            password: str
    ) -> Optional[str]:
        """
        Authenticate user and generate token.

        :param username: User's username
        :param password: User's password
        :return: Authentication token or None
        """
        if username not in self._users:
            self.logger.warning(f"User {username} not found")
            return None

        # Verify password
        user = self._users[username]
        if not await self._verify_password(password, user['password']):
            self.logger.warning(f"Invalid credentials for {username}")
            return None

        # Generate token
        token = await self._generate_token(username, user['roles'])
        return token

    async def validate_token(self, token: str) -> bool:
        """
        Validate authentication token.

        :param token: Authentication token
        :return: Token validity status
        """
        if not self._jwt_available:
            self.logger.warning("Token validation not supported")
            return False

        try:
            from jose import jwt

            # Decode and verify token
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=['HS256']
            )

            # Check token expiration
            expiration = datetime.fromtimestamp(payload['exp'])
            if datetime.now() > expiration:
                self.logger.warning("Token expired")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return False

    async def _hash_password(self, password: str) -> str:
        """
        Securely hash password.

        :param password: Plain text password
        :return: Hashed password
        """
        try:
            import bcrypt

            # Generate salt and hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)

            return hashed.decode()

        except ImportError:
            self.logger.warning("bcrypt not installed. Using insecure hashing.")
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

    async def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against stored hash.

        :param plain_password: Plain text password
        :param hashed_password: Stored password hash
        :return: Password verification status
        """
        try:
            import bcrypt
            return bcrypt.checkpw(
                plain_password.encode(),
                hashed_password.encode()
            )

        except ImportError:
            # Fallback to insecure comparison
            import hashlib
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

    async def _generate_token(
            self,
            username: str,
            roles: list,
            expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate JWT token.

        :param username: Username
        :param roles: User roles
        :param expiration: Token expiration time in seconds
        :return: Generated token
        """
        if not self._jwt_available:
            self.logger.warning("Token generation not supported")
            return None

        try:
            from jose import jwt

            # Create token payload
            payload = {
                'sub': username,
                'roles': roles,
                'exp': datetime.now() + timedelta(seconds=expiration)
            }

            # Generate token
            token = jwt.encode(payload, self._secret_key, algorithm='HS256')

            # Store token
            self._active_tokens[token] = {
                'username': username,
                'issued_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=expiration)
            }

            return token

        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information.

        :param username: Username
        :return: User information
        """
        return self._users.get(username)

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an active token.

        :param token: Token to revoke
        :return: Revocation status
        """
        if token in self._active_tokens:
            del self._active_tokens[token]
            self.logger.info("Token revoked successfully")
            return True

        self.logger.warning("Token not found")
        return False


# Example usage
async def main():
    """
    Demonstrate authentication manager functionality.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create authentication manager
    auth_manager = AuthenticationManager()

    # Register users
    await auth_manager.register_user(
        username='admin',
        password='secure_password',
        roles=['admin', 'user']
    )

    await auth_manager.register_user(
        username='user',
        password='user_password',
        roles=['user']
    )

    # Authenticate and get token
    token = await auth_manager.authenticate('admin', 'secure_password')

    if token:
        print("Authentication successful!")
        print("Token:", token)

        # Validate token
        is_valid = await auth_manager.validate_token(token)
        print("Token valid:", is_valid)

        # Get user info
        user_info = auth_manager.get_user_info('admin')
        print("User Info:", user_info)

        # Revoke token
        await auth_manager.revoke_token(token)

        # Try invalid authentication
    invalid_token = await auth_manager.authenticate('admin', 'wrong_password')
    print("Invalid authentication:", invalid_token)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())