"""
Encryption utilities for sensitive data
Uses Fernet (symmetric encryption) for secrets
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            encryption_key: Base64-encoded Fernet key. If None, generates from ENCRYPTION_KEY env var
        """
        if encryption_key:
            # Use provided key
            self.key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        else:
            # Get from environment or generate
            env_key = os.environ.get('ENCRYPTION_KEY')
            if env_key:
                self.key = env_key.encode()
            else:
                # Generate new key (should be set in production!)
                logger.warning("ENCRYPTION_KEY not set, generating new key. This should be set in production!")
                self.key = Fernet.generate_key()
        
        # Ensure key is proper length for Fernet
        if len(self.key) != 44:  # Fernet keys are 44 bytes when base64 encoded
            # Derive key from password using PBKDF2
            self.key = self._derive_key_from_password(self.key)
        
        self.cipher_suite = Fernet(self.key)
    
    def _derive_key_from_password(self, password: bytes) -> bytes:
        """Derive Fernet key from password using PBKDF2"""
        # Use a fixed salt (in production, store salt separately)
        salt = os.environ.get('ENCRYPTION_SALT', 'omnify-encryption-salt-2024').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        try:
            if not plaintext:
                return ""
            
            encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string"""
        try:
            if not ciphertext:
                return ""
            
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_bytes(self, plaintext: bytes) -> bytes:
        """Encrypt bytes"""
        try:
            return self.cipher_suite.encrypt(plaintext)
        except Exception as e:
            logger.error(f"Error encrypting bytes: {e}")
            raise
    
    def decrypt_bytes(self, ciphertext: bytes) -> bytes:
        """Decrypt bytes"""
        try:
            return self.cipher_suite.decrypt(ciphertext)
        except Exception as e:
            logger.error(f"Error decrypting bytes: {e}")
            raise


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_secret(plaintext: str) -> str:
    """Convenience function to encrypt a secret"""
    return get_encryption_manager().encrypt(plaintext)


def decrypt_secret(ciphertext: str) -> str:
    """Convenience function to decrypt a secret"""
    return get_encryption_manager().decrypt(ciphertext)

