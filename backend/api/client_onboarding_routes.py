"""
Client Onboarding API Routes
Handles client onboarding, file uploads, credential storage, and platform connections
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.models.client_onboarding_models import (
    ClientProfile, ClientProfileCreate, ClientProfileUpdate,
    FileUploadResponse, FileCategory, CredentialStoreRequest,
    CampaignIdea, CampaignIdeaCreate, OnboardingStatusResponse
)
from backend.services.client_onboarding_service import get_client_onboarding_service, ClientOnboardingService
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api/client-onboarding", tags=["client-onboarding"])

# Database dependency
def get_database() -> AsyncIOMotorDatabase:
    """Get database connection"""
    from agentkit_server import db
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    return db


# ========== CLIENT PROFILE ENDPOINTS ==========

@router.post("/profiles", response_model=ClientProfile, status_code=status.HTTP_201_CREATED)
async def create_client_profile(
    profile_data: ClientProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new client profile for onboarding"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        user_id = current_user.get("user_id")
        
        if not organization_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        profile = await service.create_client_profile(
            organization_id=organization_id,
            user_id=user_id,
            profile_data=profile_data
        )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create client profile: {str(e)}"
        )


@router.get("/profiles/{client_id}", response_model=ClientProfile)
async def get_client_profile(
    client_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get client profile by ID"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        profile = await service.get_client_profile(client_id, organization_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client profile not found"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get client profile: {str(e)}"
        )


@router.put("/profiles/{client_id}", response_model=ClientProfile)
async def update_client_profile(
    client_id: str,
    update_data: ClientProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update client profile"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        profile = await service.update_client_profile(
            client_id=client_id,
            organization_id=organization_id,
            update_data=update_data
        )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update client profile: {str(e)}"
        )


@router.get("/profiles", response_model=List[ClientProfile])
async def list_client_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List all client profiles for the organization"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        profiles = await service.list_client_profiles(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
        
        return profiles
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list client profiles: {str(e)}"
        )


# ========== FILE UPLOAD ENDPOINTS ==========

@router.post("/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    client_id: str = Form(...),
    file: UploadFile = File(...),
    file_category: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload a file (logo, creative, document, etc.) for a client"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        user_id = current_user.get("user_id")
        
        if not organization_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        # Validate file category
        try:
            category = FileCategory(file_category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file category: {file_category}. Valid categories: {[c.value for c in FileCategory]}"
            )
        
        uploaded_file = await service.upload_file(
            client_id=client_id,
            organization_id=organization_id,
            user_id=user_id,
            file=file,
            file_category=category
        )
        
        return FileUploadResponse(
            file_id=uploaded_file.file_id,
            file_name=uploaded_file.file_name,
            file_url=uploaded_file.file_url,
            file_size=uploaded_file.file_size,
            file_category=uploaded_file.file_category.value,
            uploaded_at=uploaded_file.uploaded_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/files", response_model=List[Dict[str, Any]])
async def list_client_files(
    client_id: str = Query(...),
    file_category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List files for a client"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        category = FileCategory(file_category) if file_category else None
        
        files = await service.list_client_files(
            client_id=client_id,
            organization_id=organization_id,
            file_category=category
        )
        
        return [file.dict() for file in files]
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    client_id: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a file"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        await service.delete_file(
            file_id=file_id,
            client_id=client_id,
            organization_id=organization_id
        )
        
        return {"success": True, "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


# ========== CREDENTIALS ENDPOINTS ==========

@router.post("/credentials", status_code=status.HTTP_201_CREATED)
async def store_platform_credentials(
    client_id: str = Query(...),
    credentials: CredentialStoreRequest = Depends(),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Store platform credentials securely"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        credential = await service.store_platform_credentials(
            client_id=client_id,
            organization_id=organization_id,
            credentials=credentials
        )
        
        return {
            "success": True,
            "message": f"Credentials stored for {credentials.platform}",
            "platform": credential.platform,
            "account_id": credential.account_id,
            "connection_status": credential.connection_status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store credentials: {str(e)}"
        )


@router.post("/credentials/test")
async def test_platform_connection(
    client_id: str = Query(...),
    platform: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Test platform connection using stored credentials"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        result = await service.test_platform_connection(
            client_id=client_id,
            organization_id=organization_id,
            platform=platform
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test connection: {str(e)}"
        )


# ========== CAMPAIGN IDEAS ENDPOINTS ==========

@router.post("/campaign-ideas", response_model=CampaignIdea, status_code=status.HTTP_201_CREATED)
async def create_campaign_idea(
    client_id: str = Query(...),
    idea_data: CampaignIdeaCreate = Depends(),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a campaign idea for a client"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        user_id = current_user.get("user_id")
        
        if not organization_id or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        idea = await service.create_campaign_idea(
            client_id=client_id,
            organization_id=organization_id,
            user_id=user_id,
            idea_data=idea_data
        )
        
        return idea
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign idea: {str(e)}"
        )


@router.get("/campaign-ideas", response_model=List[CampaignIdea])
async def list_campaign_ideas(
    client_id: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List campaign ideas for a client"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        ideas = await service.list_campaign_ideas(
            client_id=client_id,
            organization_id=organization_id
        )
        
        return ideas
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaign ideas: {str(e)}"
        )


# ========== ONBOARDING STATUS ENDPOINTS ==========

@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    client_id: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get onboarding status and next steps"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        status_data = await service.get_onboarding_status(
            client_id=client_id,
            organization_id=organization_id
        )
        
        return OnboardingStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get onboarding status: {str(e)}"
        )


@router.get("/next-steps")
async def get_next_steps(
    client_id: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get next steps for client onboarding"""
    try:
        service = get_client_onboarding_service(db)
        organization_id = current_user.get("organization_id")
        
        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User organization not found"
            )
        
        status_data = await service.get_onboarding_status(
            client_id=client_id,
            organization_id=organization_id
        )
        
        return {
            "client_id": client_id,
            "current_stage": status_data["onboarding_status"],
            "next_steps": [
                {"step": step, "priority": "high" if i < 3 else "medium"}
                for i, step in enumerate(status_data["next_steps"])
            ],
            "recommendations": status_data.get("recommendations", []),
            "blockers": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get next steps: {str(e)}"
        )

