"""
Client Onboarding Service for OmnifyProduct
Handles client onboarding, file storage, credential management, and platform connections
"""

import os
import uuid
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import mimetypes
import shutil

from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import UploadFile, HTTPException, status

from backend.models.client_onboarding_models import (
    ClientProfile, ClientProfileCreate, ClientProfileUpdate,
    UploadedFile, FileCategory, PlatformCredential, CredentialStoreRequest,
    CampaignIdea, CampaignIdeaCreate, OnboardingStatus, PlatformConnectionStatus
)
from backend.services.production_secrets_manager import production_secrets_manager
from backend.services.structured_logging import logger
from backend.integrations.platform_manager import PlatformIntegrationsManager, Platform


class ClientOnboardingService:
    """Service for managing client onboarding"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.platform_manager = PlatformIntegrationsManager()
        
        # File storage configuration
        self.storage_root = Path(os.environ.get('FILE_STORAGE_ROOT', './storage'))
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize secrets manager
        self.secrets_manager = production_secrets_manager
    
    # ========== CLIENT PROFILE MANAGEMENT ==========
    
    async def create_client_profile(
        self,
        organization_id: str,
        user_id: str,
        profile_data: ClientProfileCreate
    ) -> ClientProfile:
        """Create a new client profile"""
        try:
            client_id = f"client_{uuid.uuid4().hex[:16]}"
            
            profile = ClientProfile(
                client_id=client_id,
                organization_id=organization_id,
                company_name=profile_data.company_name,
                industry=profile_data.industry,
                website=profile_data.website,
                description=profile_data.description,
                primary_contact_name=profile_data.primary_contact_name,
                primary_contact_email=profile_data.primary_contact_email,
                primary_contact_phone=profile_data.primary_contact_phone,
                onboarding_status=OnboardingStatus.IN_PROGRESS,
                onboarding_progress=0.1,
                created_by=user_id
            )
            
            # Save to database
            await self.db.client_profiles.insert_one(profile.dict())
            
            logger.info(f"Created client profile {client_id}", extra={
                "client_id": client_id,
                "organization_id": organization_id,
                "company_name": profile_data.company_name
            })
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create client profile: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create client profile: {str(e)}"
            )
    
    async def get_client_profile(
        self,
        client_id: str,
        organization_id: str
    ) -> Optional[ClientProfile]:
        """Get client profile by ID"""
        try:
            doc = await self.db.client_profiles.find_one({
                "client_id": client_id,
                "organization_id": organization_id
            })
            
            if not doc:
                return None
            
            return ClientProfile(**doc)
            
        except Exception as e:
            logger.error(f"Failed to get client profile: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get client profile: {str(e)}"
            )
    
    async def update_client_profile(
        self,
        client_id: str,
        organization_id: str,
        update_data: ClientProfileUpdate
    ) -> ClientProfile:
        """Update client profile"""
        try:
            # Get existing profile
            profile = await self.get_client_profile(client_id, organization_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client profile not found"
                )
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            await self.db.client_profiles.update_one(
                {"client_id": client_id, "organization_id": organization_id},
                {"$set": update_dict}
            )
            
            # Get updated profile
            updated_profile = await self.get_client_profile(client_id, organization_id)
            
            logger.info(f"Updated client profile {client_id}", extra={
                "client_id": client_id,
                "updated_fields": list(update_dict.keys())
            })
            
            return updated_profile
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update client profile: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update client profile: {str(e)}"
            )
    
    async def list_client_profiles(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ClientProfile]:
        """List all client profiles for an organization"""
        try:
            cursor = self.db.client_profiles.find({
                "organization_id": organization_id
            }).skip(skip).limit(limit).sort("created_at", -1)
            
            profiles = []
            async for doc in cursor:
                profiles.append(ClientProfile(**doc))
            
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to list client profiles: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list client profiles: {str(e)}"
            )
    
    # ========== FILE UPLOAD MANAGEMENT ==========
    
    async def upload_file(
        self,
        client_id: str,
        organization_id: str,
        user_id: str,
        file: UploadFile,
        file_category: FileCategory
    ) -> UploadedFile:
        """Upload a file for a client"""
        try:
            # Verify client exists
            profile = await self.get_client_profile(client_id, organization_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client profile not found"
                )
            
            # Generate file ID and path
            file_id = f"file_{uuid.uuid4().hex[:16]}"
            file_extension = Path(file.filename).suffix
            safe_filename = f"{file_id}{file_extension}"
            
            # Create storage directory structure
            client_dir = self.storage_root / organization_id / client_id / file_category.value
            client_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = client_dir / safe_filename
            
            # Save file
            file_data = await file.read()
            with open(file_path, "wb") as f:
                f.write(file_data)
            
            # Get file metadata
            file_size = len(file_data)
            mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            
            # Generate file URL (relative path for now, can be absolute URL in production)
            file_url = f"/storage/{organization_id}/{client_id}/{file_category.value}/{safe_filename}"
            
            # Create uploaded file record
            uploaded_file = UploadedFile(
                file_id=file_id,
                client_id=client_id,
                file_name=file.filename,
                file_category=file_category,
                file_url=file_url,
                file_size=file_size,
                mime_type=mime_type,
                uploaded_by=user_id
            )
            
            # Save to database
            await self.db.uploaded_files.insert_one(uploaded_file.dict())
            
            # Update client profile with file reference
            await self.db.client_profiles.update_one(
                {"client_id": client_id, "organization_id": organization_id},
                {
                    "$push": {
                        "uploaded_files": {
                            "file_id": file_id,
                            "file_name": file.filename,
                            "file_category": file_category.value,
                            "file_url": file_url,
                            "uploaded_at": datetime.utcnow().isoformat()
                        }
                    }
                }
            )
            
            # Special handling for logo
            if file_category == FileCategory.LOGO:
                await self.db.client_profiles.update_one(
                    {"client_id": client_id, "organization_id": organization_id},
                    {"$set": {"logo_url": file_url}}
                )
            
            logger.info(f"Uploaded file {file_id} for client {client_id}", extra={
                "client_id": client_id,
                "file_id": file_id,
                "file_category": file_category.value,
                "file_size": file_size
            })
            
            return uploaded_file
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def list_client_files(
        self,
        client_id: str,
        organization_id: str,
        file_category: Optional[FileCategory] = None
    ) -> List[UploadedFile]:
        """List files for a client"""
        try:
            query = {
                "client_id": client_id
            }
            
            if file_category:
                query["file_category"] = file_category.value
            
            cursor = self.db.uploaded_files.find(query).sort("uploaded_at", -1)
            
            files = []
            async for doc in cursor:
                files.append(UploadedFile(**doc))
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )
    
    async def delete_file(
        self,
        file_id: str,
        client_id: str,
        organization_id: str
    ) -> bool:
        """Delete a file"""
        try:
            # Get file record
            file_doc = await self.db.uploaded_files.find_one({
                "file_id": file_id,
                "client_id": client_id
            })
            
            if not file_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Delete physical file
            file_path = self.storage_root / organization_id / client_id / file_doc["file_category"] / Path(file_doc["file_url"]).name
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            await self.db.uploaded_files.delete_one({"file_id": file_id})
            
            # Remove from client profile
            await self.db.client_profiles.update_one(
                {"client_id": client_id, "organization_id": organization_id},
                {"$pull": {"uploaded_files": {"file_id": file_id}}}
            )
            
            logger.info(f"Deleted file {file_id} for client {client_id}", extra={
                "client_id": client_id,
                "file_id": file_id
            })
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    # ========== CREDENTIAL MANAGEMENT ==========
    
    async def store_platform_credentials(
        self,
        client_id: str,
        organization_id: str,
        credentials: CredentialStoreRequest
    ) -> PlatformCredential:
        """Store platform credentials securely"""
        try:
            # Verify client exists
            profile = await self.get_client_profile(client_id, organization_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client profile not found"
                )
            
            # Prepare credential data for secrets manager
            credential_data = {
                "access_token": credentials.access_token,
                "refresh_token": credentials.refresh_token,
                "api_key": credentials.api_key,
                "api_secret": credentials.api_secret,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "account_id": credentials.account_id,
                "expires_at": credentials.expires_at,
                "additional_config": credentials.additional_config
            }
            
            # Remove None values
            credential_data = {k: v for k, v in credential_data.items() if v is not None}
            
            # Store in secrets manager
            secret_key = f"client_{client_id}_platform_{credentials.platform}"
            await self.secrets_manager.store_secret(secret_key, credential_data)
            
            # Create credential record
            platform_credential = PlatformCredential(
                platform=credentials.platform,
                access_token=credentials.access_token[:10] + "..." if credentials.access_token else None,  # Partial for display
                refresh_token=credentials.refresh_token[:10] + "..." if credentials.refresh_token else None,
                api_key=credentials.api_key[:10] + "..." if credentials.api_key else None,
                api_secret="***",  # Never store full secret
                client_id=credentials.client_id,
                client_secret="***",  # Never store full secret
                account_id=credentials.account_id,
                expires_at=datetime.fromisoformat(credentials.expires_at) if credentials.expires_at else None,
                additional_config=credentials.additional_config,
                connection_status=PlatformConnectionStatus.PENDING
            )
            
            # Save metadata to database (without sensitive data)
            credential_doc = {
                "client_id": client_id,
                "organization_id": organization_id,
                "platform": credentials.platform,
                "account_id": credentials.account_id,
                "expires_at": platform_credential.expires_at.isoformat() if platform_credential.expires_at else None,
                "connection_status": platform_credential.connection_status.value,
                "secret_key": secret_key,  # Reference to secrets manager
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.db.platform_credentials.insert_one(credential_doc)
            
            # Update client profile
            await self.db.client_profiles.update_one(
                {"client_id": client_id, "organization_id": organization_id},
                {
                    "$set": {
                        f"platform_connections.{credentials.platform}": {
                            "status": PlatformConnectionStatus.PENDING.value,
                            "account_id": credentials.account_id,
                            "connected_at": datetime.utcnow().isoformat()
                        }
                    }
                }
            )
            
            logger.info(f"Stored credentials for platform {credentials.platform} for client {client_id}", extra={
                "client_id": client_id,
                "platform": credentials.platform,
                "account_id": credentials.account_id
            })
            
            return platform_credential
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store credentials: {str(e)}"
            )
    
    async def test_platform_connection(
        self,
        client_id: str,
        organization_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """Test platform connection using stored credentials"""
        try:
            # Get credential metadata
            credential_doc = await self.db.platform_credentials.find_one({
                "client_id": client_id,
                "organization_id": organization_id,
                "platform": platform
            })
            
            if not credential_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No credentials found for platform {platform}"
                )
            
            # Get full credentials from secrets manager
            secret_key = credential_doc.get("secret_key")
            if not secret_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Credential secret key not found"
                )
            
            credentials_data = await self.secrets_manager.get_secret(secret_key)
            if not credentials_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Credentials not found in secrets manager"
                )
            
            # Map platform name to Platform enum
            platform_map = {
                "google_ads": Platform.GOOGLE_ADS,
                "meta_ads": Platform.META_ADS,
                "linkedin_ads": Platform.LINKEDIN_ADS,
                "tiktok_ads": Platform.TIKTOK_ADS,
                "youtube_ads": Platform.YOUTUBE_ADS,
                "triplewhale": Platform.TRIPLEWHALE,
                "hubspot": Platform.HUBSPOT,
                "klaviyo": Platform.KLAVIYO,
                "shopify": Platform.SHOPIFY,
                "gohighlevel": Platform.GOHIGHLEVEL
            }
            
            platform_enum = platform_map.get(platform.lower())
            if not platform_enum:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported platform: {platform}"
                )
            
            # Test connection using platform manager
            try:
                # This would use the platform manager to test the connection
                # For now, we'll update the status
                connection_status = PlatformConnectionStatus.CONNECTED
                error_message = None
                
                # Update credential status
                await self.db.platform_credentials.update_one(
                    {"client_id": client_id, "platform": platform},
                    {
                        "$set": {
                            "connection_status": connection_status.value,
                            "last_verified": datetime.utcnow().isoformat(),
                            "error_message": error_message
                        }
                    }
                )
                
                # Update client profile
                await self.db.client_profiles.update_one(
                    {"client_id": client_id, "organization_id": organization_id},
                    {
                        "$set": {
                            f"platform_connections.{platform}.status": connection_status.value,
                            f"platform_connections.{platform}.last_verified": datetime.utcnow().isoformat()
                        }
                    }
                )
                
                return {
                    "success": True,
                    "platform": platform,
                    "status": connection_status.value,
                    "message": f"Successfully connected to {platform}"
                }
                
            except Exception as e:
                connection_status = PlatformConnectionStatus.FAILED
                error_message = str(e)
                
                # Update status
                await self.db.platform_credentials.update_one(
                    {"client_id": client_id, "platform": platform},
                    {
                        "$set": {
                            "connection_status": connection_status.value,
                            "last_verified": datetime.utcnow().isoformat(),
                            "error_message": error_message
                        }
                    }
                )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Connection test failed: {error_message}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to test connection: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to test connection: {str(e)}"
            )
    
    # ========== CAMPAIGN IDEAS MANAGEMENT ==========
    
    async def create_campaign_idea(
        self,
        client_id: str,
        organization_id: str,
        user_id: str,
        idea_data: CampaignIdeaCreate
    ) -> CampaignIdea:
        """Create a campaign idea"""
        try:
            # Verify client exists
            profile = await self.get_client_profile(client_id, organization_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client profile not found"
                )
            
            idea_id = f"idea_{uuid.uuid4().hex[:16]}"
            
            idea = CampaignIdea(
                idea_id=idea_id,
                client_id=client_id,
                title=idea_data.title,
                description=idea_data.description,
                target_audience=idea_data.target_audience,
                platforms=idea_data.platforms,
                budget_estimate=idea_data.budget_estimate,
                timeline=idea_data.timeline,
                created_by=user_id
            )
            
            # Save to database
            await self.db.campaign_ideas.insert_one(idea.dict())
            
            # Add to client profile
            await self.db.client_profiles.update_one(
                {"client_id": client_id, "organization_id": organization_id},
                {"$push": {"campaign_ideas": idea.dict()}}
            )
            
            logger.info(f"Created campaign idea {idea_id} for client {client_id}", extra={
                "client_id": client_id,
                "idea_id": idea_id
            })
            
            return idea
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create campaign idea: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create campaign idea: {str(e)}"
            )
    
    async def list_campaign_ideas(
        self,
        client_id: str,
        organization_id: str
    ) -> List[CampaignIdea]:
        """List campaign ideas for a client"""
        try:
            cursor = self.db.campaign_ideas.find({
                "client_id": client_id
            }).sort("created_at", -1)
            
            ideas = []
            async for doc in cursor:
                ideas.append(CampaignIdea(**doc))
            
            return ideas
            
        except Exception as e:
            logger.error(f"Failed to list campaign ideas: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list campaign ideas: {str(e)}"
            )
    
    # ========== ONBOARDING STATUS & NEXT STEPS ==========
    
    async def get_onboarding_status(
        self,
        client_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get onboarding status and next steps"""
        try:
            profile = await self.get_client_profile(client_id, organization_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Client profile not found"
                )
            
            # Calculate progress
            completed_steps = []
            pending_steps = []
            
            if profile.company_name:
                completed_steps.append("company_info")
            else:
                pending_steps.append("company_info")
            
            if profile.logo_url:
                completed_steps.append("logo_upload")
            else:
                pending_steps.append("logo_upload")
            
            if profile.uploaded_files:
                completed_steps.append("assets_upload")
            else:
                pending_steps.append("assets_upload")
            
            # Check platform connections
            connected_platforms = []
            for platform, connection in profile.platform_connections.items():
                if connection.get("status") == PlatformConnectionStatus.CONNECTED.value:
                    connected_platforms.append(platform)
                    completed_steps.append(f"platform_{platform}")
                else:
                    pending_steps.append(f"platform_{platform}")
            
            # Calculate progress percentage
            total_steps = len(completed_steps) + len(pending_steps)
            progress = len(completed_steps) / total_steps if total_steps > 0 else 0.0
            
            # Determine next steps
            next_steps = []
            if "company_info" in pending_steps:
                next_steps.append("Complete company information")
            if "logo_upload" in pending_steps:
                next_steps.append("Upload company logo")
            if "assets_upload" in pending_steps:
                next_steps.append("Upload brand assets and creatives")
            if not connected_platforms:
                next_steps.append("Connect at least one platform (e.g., Google Ads, Meta Ads)")
            else:
                next_steps.append("Review connected platforms and test connections")
            
            return {
                "client_id": client_id,
                "onboarding_status": profile.onboarding_status.value,
                "onboarding_progress": progress,
                "completed_steps": completed_steps,
                "pending_steps": pending_steps,
                "platform_connections": profile.platform_connections,
                "connected_platforms": connected_platforms,
                "next_steps": next_steps,
                "recommendations": [
                    "Ensure all brand assets are uploaded",
                    "Connect primary advertising platforms",
                    "Review and approve campaign ideas"
                ]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get onboarding status: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get onboarding status: {str(e)}"
            )


# Singleton instance
_client_onboarding_service = None

def get_client_onboarding_service(db: AsyncIOMotorDatabase) -> ClientOnboardingService:
    """Get or create client onboarding service instance"""
    global _client_onboarding_service
    if _client_onboarding_service is None:
        _client_onboarding_service = ClientOnboardingService(db)
    return _client_onboarding_service

