"""
encryption.py
"""

import base64
import logging
from typing import Union, Optional


class EncryptionManager:
    """
    Advanced encryption and decryption utility for UnitAPI.
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encryption manager.

        :param secret_key: Optional custom encryption key
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Check cryptography library availability
        try:
            from cryptography.fernet import Fernet
            self._fernet_available = True
        except ImportError:
            self.logger.warning("Cryptography library not installed. Fallback to basic encryption.")
            self._fernet_available = False

        # Generate or use provided secret key
        self._secret_key = secret_key or self._generate_key()

    def _generate_key(self) -> str:
        """
        Generate a secure encryption key.

        :return: Generated encryption key
        """
        try:
            from cryptography.fernet import Fernet
            return Fernet.generate_key().decode()
        except ImportError:
            import secrets
            return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using Fernet symmetric encryption.

        :param data: Data to encrypt
        :return: Encrypted data as base64 encoded string
        """
        # Ensure data is in bytes
        if isinstance(data, str):
            data = data.encode()

        if self._fernet_available:
            try:
                from cryptography.fernet import Fernet
                f = Fernet(self._secret_key.encode())
                encrypted = f.encrypt(data)
                return encrypted.decode()
            except Exception as e:
                self.logger.error(f"Encryption failed: {e}")
                return self._fallback_encrypt(data)
        else:
            return self._fallback_encrypt(data)

    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """
        Decrypt data using Fernet symmetric encryption.

        :param encrypted_data: Encrypted data to decrypt
        :return: Decrypted data as string
        """
        # Ensure data is in bytes
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()

        if self._fernet_available:
            try:
                from cryptography.fernet import Fernet
                f = Fernet(self._secret_key.encode())
                decrypted = f.decrypt(encrypted_data)
                return decrypted.decode()
            except Exception as e:
                self.logger.error(f"Decryption failed: {e}")
                return self._fallback_decrypt(encrypted_data)
        else:
            return self._fallback_decrypt(encrypted_data)

    def _fallback_encrypt(self, data: bytes) -> str:
        """
        Fallback basic encryption method.

        :param data: Data to encrypt
        :return: Encrypted data
        """
        # Simple XOR encryption with secret key
        key_bytes = self._secret_key.encode()
        encrypted = bytearray()

        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return base64.urlsafe_b64encode(encrypted).decode()

    def _fallback_decrypt(self, encrypted_data: bytes) -> str:
        """
        Fallback basic decryption method.

        :param encrypted_data: Data to decrypt
        :return: Decrypted data
        """
        # Decode base64
        decoded = base64.urlsafe_b64decode(encrypted_data)

        # Simple XOR decryption
        key_bytes = self._secret_key.encode()
        decrypted = bytearray()

        for i, byte in enumerate(decoded):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return bytes(decrypted).decode()

    def generate_secure_random(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random string.

        :param length: Length of random string
        :return: Random string
        """
        import secrets
        return secrets.token_urlsafe(length)

    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Create a secure hash of the input data.

        :param data: Data to hash
        :param algorithm: Hashing algorithm
        :return: Hashed data
        """
        import hashlib

        # Ensure data is in bytes
        if isinstance(data, str):
            data = data.encode()

        # Select hashing algorithm
        hash_func = getattr(hashlib, algorithm)()
        hash_func.update(data)

        return hash_func.hexdigest()


# Example usage
def main():
    """
    Demonstrate encryption manager functionality.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create encryption manager
    encryption_manager = EncryptionManager()

    # Original data
    original_data = "Sensitive information for UnitAPI"
    print("Original Data:", original_data)

    # Encrypt data
    encrypted = encryption_manager.encrypt(original_data)
    print("Encrypted Data:", encrypted)

    # Decrypt data
    decrypted = encryption_manager.decrypt(encrypted)
    print("Decrypted Data:", decrypted)

    # Generate random token
    random_token = encryption_manager.generate_secure_random()
    print("Random Token:", random_token)

    # Hash data
    hashed_data = encryption_manager.hash_data(original_data)
    print("Hashed Data:", hashed_data)


if __name__ == "__main__":
    main()