"""
Secrets Management Service
Supports AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, and local environment variables
"""

import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SecretsManagerType(str, Enum):
    """Supported secrets manager types"""
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    AZURE_KEY_VAULT = "azure_key_vault"
    ENVIRONMENT = "environment"  # Fallback to environment variables


class SecretsManager:
    """Unified secrets manager interface"""
    
    def __init__(self, manager_type: Optional[SecretsManagerType] = None):
        """
        Initialize secrets manager
        
        Args:
            manager_type: Type of secrets manager to use. If None, auto-detects from environment.
        """
        self.manager_type = manager_type or self._detect_manager_type()
        self.client = self._initialize_client()
        logger.info(f"Secrets manager initialized: {self.manager_type.value}")
    
    def _detect_manager_type(self) -> SecretsManagerType:
        """Auto-detect secrets manager type from environment"""
        if os.getenv("AWS_SECRETS_MANAGER_REGION"):
            return SecretsManagerType.AWS_SECRETS_MANAGER
        elif os.getenv("VAULT_ADDR"):
            return SecretsManagerType.HASHICORP_VAULT
        elif os.getenv("AZURE_KEY_VAULT_URL"):
            return SecretsManagerType.AZURE_KEY_VAULT
        else:
            return SecretsManagerType.ENVIRONMENT
    
    def _initialize_client(self):
        """Initialize the appropriate secrets manager client"""
        if self.manager_type == SecretsManagerType.AWS_SECRETS_MANAGER:
            return self._init_aws_secrets_manager()
        elif self.manager_type == SecretsManagerType.HASHICORP_VAULT:
            return self._init_vault()
        elif self.manager_type == SecretsManagerType.AZURE_KEY_VAULT:
            return self._init_azure_key_vault()
        else:
            return None  # Environment variables don't need a client
    
    def _init_aws_secrets_manager(self):
        """Initialize AWS Secrets Manager client"""
        try:
            import boto3
            region = os.getenv("AWS_SECRETS_MANAGER_REGION", "us-east-1")
            return boto3.client('secretsmanager', region_name=region)
        except ImportError:
            logger.warning("boto3 not installed, AWS Secrets Manager unavailable")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize AWS Secrets Manager: {e}")
            return None
    
    def _init_vault(self):
        """Initialize HashiCorp Vault client"""
        try:
            import hvac
            vault_addr = os.getenv("VAULT_ADDR")
            vault_token = os.getenv("VAULT_TOKEN")
            
            if not vault_addr:
                logger.warning("VAULT_ADDR not set, HashiCorp Vault unavailable")
                return None
            
            client = hvac.Client(url=vault_addr, token=vault_token)
            return client
        except ImportError:
            logger.warning("hvac not installed, HashiCorp Vault unavailable")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize HashiCorp Vault: {e}")
            return None
    
    def _init_azure_key_vault(self):
        """Initialize Azure Key Vault client"""
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            if not vault_url:
                logger.warning("AZURE_KEY_VAULT_URL not set, Azure Key Vault unavailable")
                return None
            
            credential = DefaultAzureCredential()
            return SecretClient(vault_url=vault_url, credential=credential)
        except ImportError:
            logger.warning("azure-keyvault-secrets not installed, Azure Key Vault unavailable")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Azure Key Vault: {e}")
            return None
    
    def get_secret(self, secret_name: str, required: bool = True) -> Optional[str]:
        """
        Get secret value
        
        Args:
            secret_name: Name of the secret
            required: If True, raises error if secret not found. If False, returns None.
            
        Returns:
            Secret value or None if not found and not required
            
        Raises:
            ValueError: If secret is required but not found
        """
        try:
            if self.manager_type == SecretsManagerType.AWS_SECRETS_MANAGER:
                return self._get_aws_secret(secret_name)
            elif self.manager_type == SecretsManagerType.HASHICORP_VAULT:
                return self._get_vault_secret(secret_name)
            elif self.manager_type == SecretsManagerType.AZURE_KEY_VAULT:
                return self._get_azure_secret(secret_name)
            else:
                # Fallback to environment variables
                value = os.getenv(secret_name)
                if value:
                    return value
                elif required:
                    raise ValueError(f"Required secret '{secret_name}' not found in environment variables")
                else:
                    return None
        except Exception as e:
            if required:
                raise ValueError(f"Failed to get secret '{secret_name}': {e}")
            else:
                logger.warning(f"Failed to get secret '{secret_name}': {e}")
                return None
    
    def _get_aws_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager"""
        if not self.client:
            raise ValueError("AWS Secrets Manager client not initialized")
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except self.client.exceptions.ResourceNotFoundException:
            raise ValueError(f"Secret '{secret_name}' not found in AWS Secrets Manager")
        except Exception as e:
            raise ValueError(f"Failed to get secret from AWS Secrets Manager: {e}")
    
    def _get_vault_secret(self, secret_name: str) -> str:
        """Get secret from HashiCorp Vault"""
        if not self.client:
            raise ValueError("HashiCorp Vault client not initialized")
        
        try:
            # Parse secret path (format: secret/path/to/secret)
            parts = secret_name.split('/', 1)
            if len(parts) == 1:
                mount_point = "secret"
                path = parts[0]
            else:
                mount_point = parts[0]
                path = parts[1]
            
            response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount_point)
            return response['data']['data'].get(path.split('/')[-1], '')
        except Exception as e:
            raise ValueError(f"Failed to get secret from Vault: {e}")
    
    def _get_azure_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault"""
        if not self.client:
            raise ValueError("Azure Key Vault client not initialized")
        
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            raise ValueError(f"Failed to get secret from Azure Key Vault: {e}")
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Set secret value (for supported managers)
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.manager_type == SecretsManagerType.AWS_SECRETS_MANAGER:
                return self._set_aws_secret(secret_name, secret_value)
            elif self.manager_type == SecretsManagerType.HASHICORP_VAULT:
                return self._set_vault_secret(secret_name, secret_value)
            elif self.manager_type == SecretsManagerType.AZURE_KEY_VAULT:
                return self._set_azure_secret(secret_name, secret_value)
            else:
                # For environment variables, we can't set them programmatically
                logger.warning("Cannot set secrets in environment variable mode")
                return False
        except Exception as e:
            logger.error(f"Failed to set secret '{secret_name}': {e}")
            return False
    
    def _set_aws_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in AWS Secrets Manager"""
        if not self.client:
            return False
        
        try:
            # Try to update existing secret
            try:
                self.client.update_secret(SecretId=secret_name, SecretString=secret_value)
            except self.client.exceptions.ResourceNotFoundException:
                # Create new secret if it doesn't exist
                self.client.create_secret(Name=secret_name, SecretString=secret_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set AWS secret: {e}")
            return False
    
    def _set_vault_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in HashiCorp Vault"""
        if not self.client:
            return False
        
        try:
            parts = secret_name.split('/', 1)
            if len(parts) == 1:
                mount_point = "secret"
                path = parts[0]
            else:
                mount_point = parts[0]
                path = parts[1]
            
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={path.split('/')[-1]: secret_value},
                mount_point=mount_point
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set Vault secret: {e}")
            return False
    
    def _set_azure_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Azure Key Vault"""
        if not self.client:
            return False
        
        try:
            self.client.set_secret(secret_name, secret_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set Azure secret: {e}")
            return False


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_required_secret(secret_name: str) -> str:
    """
    Get required secret (raises error if not found)
    
    Args:
        secret_name: Name of the secret
        
    Returns:
        Secret value
        
    Raises:
        ValueError: If secret not found
    """
    manager = get_secrets_manager()
    value = manager.get_secret(secret_name, required=True)
    if value is None:
        raise ValueError(f"Required secret '{secret_name}' not found")
    return value

