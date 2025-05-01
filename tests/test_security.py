"""
Tests for the security modules in UnitAPI.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.unitapi.security.access_control import AccessControlManager, AccessLevel
from src.unitapi.security.authentication import AuthenticationManager
from src.unitapi.security.encryption import EncryptionManager


class TestAccessControlManager:
    """Test cases for the AccessControlManager."""

    @pytest.fixture
    def acl_manager(self):
        """Create an AccessControlManager instance for testing."""
        return AccessControlManager()

    def test_define_role(self, acl_manager):
        """Test defining a new role."""
        # Define a new role
        permissions = {
            "devices": AccessLevel.READ,
            "system": AccessLevel.NONE,
            "network": AccessLevel.NONE,
        }
        acl_manager.define_role("guest", permissions)

        # Check if the role was added
        assert "guest" in acl_manager._role_permissions
        assert acl_manager._role_permissions["guest"] == permissions

    def test_add_resource_rule(self, acl_manager):
        """Test adding a resource-specific access rule."""
        # Add a resource rule
        acl_manager.add_resource_rule("light_sensor", "read", ["admin", "operator"])

        # Check if the rule was added
        assert "light_sensor" in acl_manager._resource_access
        assert "read" in acl_manager._resource_access["light_sensor"]
        assert acl_manager._resource_access["light_sensor"]["read"] == [
            "admin",
            "operator",
        ]

    def test_add_dynamic_rule(self, acl_manager):
        """Test adding a dynamic access control rule."""

        # Create a dynamic rule
        def test_rule(role, resource, action, context=None):
            return role == "admin"

        # Add the rule
        acl_manager.add_dynamic_rule(test_rule)

        # Check if the rule was added
        assert test_rule in acl_manager._dynamic_rules

    def test_check_access_unknown_role(self, acl_manager):
        """Test check_access with an unknown role."""
        # Check access with an unknown role
        result = acl_manager.check_access("unknown", "temperature_sensor", "read")

        # Should return False for unknown roles
        assert result is False

    def test_check_access_resource_rule_allowed(self, acl_manager):
        """Test check_access with a resource rule that allows access."""
        # Add a resource rule
        acl_manager.add_resource_rule("light_sensor", "read", ["admin", "operator"])

        # Check access with a role that has permission
        result = acl_manager.check_access("admin", "light_sensor", "read")

        # Should return True
        assert result is True

    def test_check_access_resource_rule_denied(self, acl_manager):
        """Test check_access with a resource rule that denies access."""
        # Add a resource rule
        acl_manager.add_resource_rule("light_sensor", "read", ["admin", "operator"])

        # Check access with a role that doesn't have permission
        result = acl_manager.check_access("viewer", "light_sensor", "read")

        # Should return False
        assert result is False

    def test_check_access_dynamic_rule_allowed(self, acl_manager):
        """Test check_access with a dynamic rule that allows access."""

        # Add a dynamic rule that allows access for admin
        def test_rule(role, resource, action, context=None):
            return role == "admin"

        acl_manager.add_dynamic_rule(test_rule)

        # Check access with admin role
        result = acl_manager.check_access("admin", "any_resource", "any_action")

        # Should return True
        assert result is True

    def test_check_access_dynamic_rule_denied(self, acl_manager):
        """Test check_access with a dynamic rule that denies access."""

        # Add a dynamic rule that denies access for non-admin
        def test_rule(role, resource, action, context=None):
            return role == "admin"

        acl_manager.add_dynamic_rule(test_rule)

        # Check access with non-admin role
        result = acl_manager.check_access("operator", "any_resource", "any_action")

        # Should return False
        assert result is False

    def test_check_access_dynamic_rule_exception(self, acl_manager):
        """Test check_access with a dynamic rule that raises an exception."""

        # Add a dynamic rule that raises an exception
        def test_rule(role, resource, action, context=None):
            raise Exception("Rule error")

        acl_manager.add_dynamic_rule(test_rule)

        # Check access
        result = acl_manager.check_access("admin", "any_resource", "any_action")

        # Should return False when a rule raises an exception
        assert result is False

    async def test_audit_access(self, acl_manager):
        """Test audit_access method."""
        # Mock the _log_audit method
        acl_manager._log_audit = MagicMock()

        # Call audit_access
        context = {"temperature": 22}
        result = await acl_manager.audit_access(
            "admin", "temperature_sensor", "write", context
        )

        # Check the result
        assert "timestamp" in result
        assert result["role"] == "admin"
        assert result["resource"] == "temperature_sensor"
        assert result["action"] == "write"
        assert result["context"] == context

        # Check that _log_audit was called
        acl_manager._log_audit.assert_called_once_with(result)


class TestAuthenticationManager:
    """Test cases for the AuthenticationManager."""

    @pytest.fixture
    def auth_manager(self):
        """Create an AuthenticationManager instance for testing."""
        return AuthenticationManager(secret_key="test-secret-key")

    def test_init(self, auth_manager):
        """Test initialization."""
        assert auth_manager._secret_key == "test-secret-key"
        assert auth_manager._users == {}
        assert auth_manager._active_tokens == {}

    @patch("src.unitapi.security.authentication.bcrypt")
    async def test_register_user_success(self, mock_bcrypt, auth_manager):
        """Test successful user registration."""
        # Setup mock
        mock_bcrypt.gensalt.return_value = b"salt"
        mock_bcrypt.hashpw.return_value = b"hashed_password"

        # Register a user
        result = await auth_manager.register_user("testuser", "password", ["user"])

        # Check the result
        assert result is True
        assert "testuser" in auth_manager._users
        assert auth_manager._users["testuser"]["password"] == "hashed_password"
        assert auth_manager._users["testuser"]["roles"] == ["user"]

    @patch("src.unitapi.security.authentication.bcrypt")
    async def test_register_user_already_exists(self, mock_bcrypt, auth_manager):
        """Test user registration when the user already exists."""
        # Setup mock
        mock_bcrypt.gensalt.return_value = b"salt"
        mock_bcrypt.hashpw.return_value = b"hashed_password"

        # Register a user
        await auth_manager.register_user("testuser", "password", ["user"])

        # Try to register the same user again
        result = await auth_manager.register_user("testuser", "password", ["user"])

        # Check the result
        assert result is False

    @patch("src.unitapi.security.authentication.bcrypt")
    async def test_authenticate_success(self, mock_bcrypt, auth_manager):
        """Test successful authentication."""
        # Setup mock
        mock_bcrypt.gensalt.return_value = b"salt"
        mock_bcrypt.hashpw.return_value = b"hashed_password"
        mock_bcrypt.checkpw.return_value = True

        # Register a user
        await auth_manager.register_user("testuser", "password", ["user"])

        # Mock the _generate_token method
        auth_manager._generate_token = MagicMock(return_value="test-token")

        # Authenticate
        token = await auth_manager.authenticate("testuser", "password")

        # Check the result
        assert token == "test-token"
        auth_manager._generate_token.assert_called_once_with("testuser", ["user"])

    @patch("src.unitapi.security.authentication.bcrypt")
    async def test_authenticate_user_not_found(self, mock_bcrypt, auth_manager):
        """Test authentication with a non-existent user."""
        # Authenticate with a non-existent user
        token = await auth_manager.authenticate("nonexistent", "password")

        # Check the result
        assert token is None

    @patch("src.unitapi.security.authentication.bcrypt")
    async def test_authenticate_invalid_password(self, mock_bcrypt, auth_manager):
        """Test authentication with an invalid password."""
        # Setup mock
        mock_bcrypt.gensalt.return_value = b"salt"
        mock_bcrypt.hashpw.return_value = b"hashed_password"
        mock_bcrypt.checkpw.return_value = False

        # Register a user
        await auth_manager.register_user("testuser", "password", ["user"])

        # Authenticate with an invalid password
        token = await auth_manager.authenticate("testuser", "wrong-password")

        # Check the result
        assert token is None

    @patch("src.unitapi.security.authentication.jwt")
    async def test_validate_token_success(self, mock_jwt, auth_manager):
        """Test successful token validation."""
        # Setup mock
        auth_manager._jwt_available = True
        mock_jwt.decode.return_value = {
            "exp": (auth_manager._generate_token.return_value + 3600).timestamp()
        }

        # Validate token
        result = await auth_manager.validate_token("test-token")

        # Check the result
        assert result is True
        mock_jwt.decode.assert_called_once_with(
            "test-token", "test-secret-key", algorithms=["HS256"]
        )

    async def test_validate_token_jwt_not_available(self, auth_manager):
        """Test token validation when JWT is not available."""
        # Setup
        auth_manager._jwt_available = False

        # Validate token
        result = await auth_manager.validate_token("test-token")

        # Check the result
        assert result is False

    @patch("src.unitapi.security.authentication.jwt")
    async def test_validate_token_exception(self, mock_jwt, auth_manager):
        """Test token validation with an exception."""
        # Setup mock
        auth_manager._jwt_available = True
        mock_jwt.decode.side_effect = Exception("Validation error")

        # Validate token
        result = await auth_manager.validate_token("test-token")

        # Check the result
        assert result is False

    def test_get_user_info(self, auth_manager):
        """Test getting user information."""
        # Add a user
        user_info = {"password": "hashed_password", "roles": ["user"]}
        auth_manager._users["testuser"] = user_info

        # Get user info
        result = auth_manager.get_user_info("testuser")

        # Check the result
        assert result == user_info

    def test_get_user_info_not_found(self, auth_manager):
        """Test getting information for a non-existent user."""
        # Get user info for a non-existent user
        result = auth_manager.get_user_info("nonexistent")

        # Check the result
        assert result is None

    async def test_revoke_token_success(self, auth_manager):
        """Test successful token revocation."""
        # Add a token
        auth_manager._active_tokens["test-token"] = {"username": "testuser"}

        # Revoke token
        result = await auth_manager.revoke_token("test-token")

        # Check the result
        assert result is True
        assert "test-token" not in auth_manager._active_tokens

    async def test_revoke_token_not_found(self, auth_manager):
        """Test revoking a non-existent token."""
        # Revoke a non-existent token
        result = await auth_manager.revoke_token("nonexistent-token")

        # Check the result
        assert result is False


class TestEncryptionManager:
    """Test cases for the EncryptionManager."""

    @pytest.fixture
    def encryption_manager(self):
        """Create an EncryptionManager instance for testing."""
        return EncryptionManager(secret_key="test-secret-key")

    def test_init(self, encryption_manager):
        """Test initialization."""
        assert encryption_manager._secret_key == "test-secret-key"

    @patch("src.unitapi.security.encryption.Fernet")
    def test_encrypt_success(self, mock_fernet, encryption_manager):
        """Test successful encryption."""
        # Setup mock
        encryption_manager._fernet_available = True
        mock_fernet_instance = MagicMock()
        mock_fernet.return_value = mock_fernet_instance
        mock_fernet_instance.encrypt.return_value = b"encrypted_data"

        # Encrypt data
        result = encryption_manager.encrypt("test-data")

        # Check the result
        assert result == "encrypted_data"
        mock_fernet.assert_called_once_with(b"test-secret-key")
        mock_fernet_instance.encrypt.assert_called_once_with(b"test-data")

    def test_encrypt_fernet_not_available(self, encryption_manager):
        """Test encryption when Fernet is not available."""
        # Setup
        encryption_manager._fernet_available = False

        # Mock the fallback method
        encryption_manager._fallback_encrypt = MagicMock(
            return_value="fallback_encrypted"
        )

        # Encrypt data
        result = encryption_manager.encrypt("test-data")

        # Check the result
        assert result == "fallback_encrypted"
        encryption_manager._fallback_encrypt.assert_called_once_with(b"test-data")

    @patch("src.unitapi.security.encryption.Fernet")
    def test_encrypt_exception(self, mock_fernet, encryption_manager):
        """Test encryption with an exception."""
        # Setup mock
        encryption_manager._fernet_available = True
        mock_fernet_instance = MagicMock()
        mock_fernet.return_value = mock_fernet_instance
        mock_fernet_instance.encrypt.side_effect = Exception("Encryption error")

        # Mock the fallback method
        encryption_manager._fallback_encrypt = MagicMock(
            return_value="fallback_encrypted"
        )

        # Encrypt data
        result = encryption_manager.encrypt("test-data")

        # Check the result
        assert result == "fallback_encrypted"
        encryption_manager._fallback_encrypt.assert_called_once_with(b"test-data")

    @patch("src.unitapi.security.encryption.Fernet")
    def test_decrypt_success(self, mock_fernet, encryption_manager):
        """Test successful decryption."""
        # Setup mock
        encryption_manager._fernet_available = True
        mock_fernet_instance = MagicMock()
        mock_fernet.return_value = mock_fernet_instance
        mock_fernet_instance.decrypt.return_value = b"decrypted_data"

        # Decrypt data
        result = encryption_manager.decrypt("encrypted_data")

        # Check the result
        assert result == "decrypted_data"
        mock_fernet.assert_called_once_with(b"test-secret-key")
        mock_fernet_instance.decrypt.assert_called_once_with(b"encrypted_data")

    def test_decrypt_fernet_not_available(self, encryption_manager):
        """Test decryption when Fernet is not available."""
        # Setup
        encryption_manager._fernet_available = False

        # Mock the fallback method
        encryption_manager._fallback_decrypt = MagicMock(
            return_value="fallback_decrypted"
        )

        # Decrypt data
        result = encryption_manager.decrypt("encrypted_data")

        # Check the result
        assert result == "fallback_decrypted"
        encryption_manager._fallback_decrypt.assert_called_once_with(b"encrypted_data")

    @patch("src.unitapi.security.encryption.Fernet")
    def test_decrypt_exception(self, mock_fernet, encryption_manager):
        """Test decryption with an exception."""
        # Setup mock
        encryption_manager._fernet_available = True
        mock_fernet_instance = MagicMock()
        mock_fernet.return_value = mock_fernet_instance
        mock_fernet_instance.decrypt.side_effect = Exception("Decryption error")

        # Mock the fallback method
        encryption_manager._fallback_decrypt = MagicMock(
            return_value="fallback_decrypted"
        )

        # Decrypt data
        result = encryption_manager.decrypt("encrypted_data")

        # Check the result
        assert result == "fallback_decrypted"
        encryption_manager._fallback_decrypt.assert_called_once_with(b"encrypted_data")

    def test_fallback_encrypt_decrypt(self, encryption_manager):
        """Test the fallback encryption and decryption methods."""
        # Encrypt data using the fallback method
        data = b"test-data"
        encrypted = encryption_manager._fallback_encrypt(data)

        # Decrypt the encrypted data
        decrypted = encryption_manager._fallback_decrypt(encrypted.encode())

        # Check that the decrypted data matches the original
        assert decrypted == "test-data"

    @patch("src.unitapi.security.encryption.secrets")
    def test_generate_secure_random(self, mock_secrets, encryption_manager):
        """Test generating a secure random string."""
        # Setup mock
        mock_secrets.token_urlsafe.return_value = "random_string"

        # Generate random string
        result = encryption_manager.generate_secure_random(16)

        # Check the result
        assert result == "random_string"
        mock_secrets.token_urlsafe.assert_called_once_with(16)

    @patch("src.unitapi.security.encryption.hashlib")
    def test_hash_data(self, mock_hashlib, encryption_manager):
        """Test hashing data."""
        # Setup mock
        mock_hash = MagicMock()
        mock_hashlib.sha256.return_value = mock_hash
        mock_hash.hexdigest.return_value = "hashed_data"

        # Hash data
        result = encryption_manager.hash_data("test-data")

        # Check the result
        assert result == "hashed_data"
        mock_hashlib.sha256.assert_called_once()
        mock_hash.update.assert_called_once_with(b"test-data")
