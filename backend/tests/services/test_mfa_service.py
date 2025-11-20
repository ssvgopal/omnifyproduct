"""
Tests for MFA Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from services.mfa_service import MFAService


@pytest.mark.asyncio
class TestMFAService:
    """Test MFA service"""
    
    async def test_setup_totp(self, mock_db, mock_user):
        """Test setup TOTP MFA"""
        service = MFAService(mock_db, "test-encryption-key-32-bytes-long!!")
        
        mock_db.mfa_secrets.find_one = AsyncMock(return_value=None)
        mock_db.mfa_secrets.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mfa_secret_123")
        )
        
        result = await service.setup_totp(mock_user["user_id"], mock_user["email"])
        
        assert result is not None
        assert "secret" in result
        assert "qr_code" in result
        assert "backup_codes" in result
    
    async def test_verify_totp(self, mock_db, mock_user):
        """Test verify TOTP code"""
        service = MFAService(mock_db)
        
        # Mock user with MFA enabled
        mock_user_with_mfa = {
            **mock_user,
            "mfa_enabled": True,
            "mfa_secret": "encrypted_secret"
        }
        
        mock_db.users.find_one = AsyncMock(return_value=mock_user_with_mfa)
        
        with patch('services.mfa_service.pyotp.TOTP', return_value=MagicMock(verify=MagicMock(return_value=True))):
            result = await service.verify_totp(mock_user["user_id"], "123456")
            
            assert result is True
    
    async def test_generate_backup_codes(self, mock_db, mock_user):
        """Test generate backup codes"""
        service = MFAService(mock_db)
        
        mock_db.users.update_one = AsyncMock(
            return_value=MagicMock(modified_count=1)
        )
        
        result = await service.generate_backup_codes(mock_user["user_id"])
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 10  # Default backup codes count

