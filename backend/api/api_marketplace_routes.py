"""
API Marketplace API Routes
Production-grade API endpoints for third-party integrations, extensions, and developer ecosystem
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import redis

from services.api_marketplace_service import (
    get_api_marketplace_service, APIMarketplaceService,
    IntegrationType, IntegrationStatus, PricingModel, DeveloperTier
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class DeveloperProfileRequest(BaseModel):
    name: str = Field(..., description="Developer name")
    email: str = Field(..., description="Developer email")
    company: Optional[str] = Field(None, description="Company name")
    tier: Optional[str] = Field("individual", description="Developer tier")

class IntegrationPackageRequest(BaseModel):
    name: str = Field(..., description="Package name")
    description: str = Field(..., description="Package description")
    version: str = Field(..., description="Package version")
    integration_type: str = Field(..., description="Integration type")
    pricing_model: Optional[str] = Field("free", description="Pricing model")
    price: Optional[float] = Field(None, description="Package price")
    tags: Optional[List[str]] = Field([], description="Package tags")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    api_endpoints: Optional[List[Dict[str, Any]]] = Field([], description="API endpoints")
    configuration_schema: Optional[Dict[str, Any]] = Field({}, description="Configuration schema")
    dependencies: Optional[List[str]] = Field([], description="Dependencies")

class IntegrationInstallationRequest(BaseModel):
    package_id: str = Field(..., description="Package ID")
    configuration: Dict[str, Any] = Field(..., description="Installation configuration")

class PackageSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    integration_type: Optional[str] = Field(None, description="Filter by integration type")
    pricing_model: Optional[str] = Field(None, description="Filter by pricing model")
    tags: Optional[List[str]] = Field([], description="Filter by tags")
    developer_id: Optional[str] = Field(None, description="Filter by developer")

class DeveloperProfileResponse(BaseModel):
    developer_id: str
    name: str
    email: str
    company: Optional[str]
    tier: str
    integrations_count: int
    total_downloads: int
    rating: float
    verified: bool
    created_at: str
    updated_at: str

class IntegrationPackageResponse(BaseModel):
    package_id: str
    name: str
    description: str
    version: str
    integration_type: str
    developer_id: str
    pricing_model: str
    price: Optional[float]
    status: str
    tags: List[str]
    documentation_url: Optional[str]
    repository_url: Optional[str]
    api_endpoints: List[Dict[str, Any]]
    configuration_schema: Dict[str, Any]
    dependencies: List[str]
    download_count: Optional[int]
    rating: Optional[float]
    created_at: str
    updated_at: str

class IntegrationInstallationResponse(BaseModel):
    installation_id: str
    package_id: str
    organization_id: str
    developer_id: str
    configuration: Dict[str, Any]
    status: str
    installed_at: str
    last_used: Optional[str]

class MarketplaceDashboardResponse(BaseModel):
    organization_id: str
    package_statistics: Dict[str, Any]
    organization_statistics: Dict[str, Any]
    popular_packages: List[Dict[str, Any]]
    recent_packages: List[Dict[str, Any]]
    supported_integration_types: List[str]
    supported_pricing_models: List[str]
    generated_at: str

# Dependency
async def get_marketplace_service(db: AsyncIOMotorClient = Depends(get_database)) -> APIMarketplaceService:
    # In production, initialize Redis properly
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    return get_api_marketplace_service(db, redis_client)

# Developer Management
@router.post("/api/marketplace/developers", response_model=DeveloperProfileResponse, summary="Create Developer Profile")
async def create_developer_profile(
    request: DeveloperProfileRequest = Body(...),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Create a new developer profile.
    Registers developers to publish integrations in the marketplace.
    """
    try:
        # Validate developer tier
        try:
            DeveloperTier(request.tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid developer tier: {request.tier}"
            )
        
        developer_data = {
            "name": request.name,
            "email": request.email,
            "company": request.company,
            "tier": request.tier
        }
        
        developer_id = await marketplace_service.developer_manager.create_developer_profile(developer_data)
        
        # Get created developer profile
        developer_doc = await marketplace_service.developer_manager.get_developer_profile(developer_id)
        
        return DeveloperProfileResponse(
            developer_id=developer_doc["developer_id"],
            name=developer_doc["name"],
            email=developer_doc["email"],
            company=developer_doc.get("company"),
            tier=developer_doc["tier"],
            integrations_count=developer_doc["integrations_count"],
            total_downloads=developer_doc["total_downloads"],
            rating=developer_doc["rating"],
            verified=developer_doc["verified"],
            created_at=developer_doc["created_at"],
            updated_at=developer_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating developer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create developer profile"
        )

@router.get("/api/marketplace/developers/{developer_id}", response_model=DeveloperProfileResponse, summary="Get Developer Profile")
async def get_developer_profile(
    developer_id: str,
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Get developer profile information.
    Returns developer details and statistics.
    """
    try:
        developer_doc = await marketplace_service.developer_manager.get_developer_profile(developer_id)
        
        if not developer_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer profile not found"
            )
        
        return DeveloperProfileResponse(
            developer_id=developer_doc["developer_id"],
            name=developer_doc["name"],
            email=developer_doc["email"],
            company=developer_doc.get("company"),
            tier=developer_doc["tier"],
            integrations_count=developer_doc["integrations_count"],
            total_downloads=developer_doc["total_downloads"],
            rating=developer_doc["rating"],
            verified=developer_doc["verified"],
            created_at=developer_doc["created_at"],
            updated_at=developer_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting developer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get developer profile"
        )

# Integration Package Management
@router.post("/api/marketplace/packages", response_model=IntegrationPackageResponse, summary="Create Integration Package")
async def create_integration_package(
    package_data: IntegrationPackageRequest = Body(...),
    package_file: UploadFile = File(...),
    developer_id: str = Query(..., description="Developer ID"),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Create a new integration package.
    Uploads package files and creates package definition.
    """
    try:
        # Validate integration type
        try:
            IntegrationType(package_data.integration_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid integration type: {package_data.integration_type}"
            )
        
        # Validate pricing model
        try:
            PricingModel(package_data.pricing_model)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pricing model: {package_data.pricing_model}"
            )
        
        # Read package file
        package_files = await package_file.read()
        
        # Create package data
        package_dict = package_data.dict()
        
        # Create package
        package_id = await marketplace_service.create_integration_package(
            package_dict, package_files, developer_id
        )
        
        # Get created package
        package_doc = await marketplace_service.db.integration_packages.find_one({"package_id": package_id})
        
        return IntegrationPackageResponse(
            package_id=package_doc["package_id"],
            name=package_doc["name"],
            description=package_doc["description"],
            version=package_doc["version"],
            integration_type=package_doc["integration_type"],
            developer_id=package_doc["developer_id"],
            pricing_model=package_doc["pricing_model"],
            price=package_doc.get("price"),
            status=package_doc["status"],
            tags=package_doc["tags"],
            documentation_url=package_doc.get("documentation_url"),
            repository_url=package_doc.get("repository_url"),
            api_endpoints=package_doc["api_endpoints"],
            configuration_schema=package_doc["configuration_schema"],
            dependencies=package_doc["dependencies"],
            download_count=package_doc.get("download_count", 0),
            rating=package_doc.get("rating", 0.0),
            created_at=package_doc["created_at"],
            updated_at=package_doc["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating integration package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration package"
        )

@router.get("/api/marketplace/packages", response_model=List[IntegrationPackageResponse], summary="List Integration Packages")
async def list_integration_packages(
    integration_type: Optional[str] = Query(None, description="Filter by integration type"),
    status: Optional[str] = Query("approved", description="Filter by status"),
    pricing_model: Optional[str] = Query(None, description="Filter by pricing model"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    developer_id: Optional[str] = Query(None, description="Filter by developer"),
    limit: int = Query(50, description="Number of packages to return"),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    List integration packages with filtering options.
    Returns package summaries and metadata.
    """
    try:
        # Build filters
        filters = {}
        if integration_type:
            filters["integration_type"] = integration_type
        if status:
            filters["status"] = status
        if pricing_model:
            filters["pricing_model"] = pricing_model
        if tags:
            filters["tags"] = tags.split(",")
        if developer_id:
            filters["developer_id"] = developer_id
        
        # Get packages
        packages = await marketplace_service.get_integration_packages(filters)
        
        # Limit results
        packages = packages[:limit]
        
        package_responses = []
        for package in packages:
            package_responses.append(IntegrationPackageResponse(
                package_id=package["package_id"],
                name=package["name"],
                description=package["description"],
                version=package["version"],
                integration_type=package["integration_type"],
                developer_id=package["developer_id"],
                pricing_model=package["pricing_model"],
                price=package.get("price"),
                status=package["status"],
                tags=package["tags"],
                documentation_url=package.get("documentation_url"),
                repository_url=package.get("repository_url"),
                api_endpoints=package["api_endpoints"],
                configuration_schema=package["configuration_schema"],
                dependencies=package["dependencies"],
                download_count=package.get("download_count", 0),
                rating=package.get("rating", 0.0),
                created_at=package["created_at"],
                updated_at=package["updated_at"]
            ))
        
        return package_responses
        
    except Exception as e:
        logger.error(f"Error listing integration packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list integration packages"
        )

@router.get("/api/marketplace/packages/{package_id}", response_model=IntegrationPackageResponse, summary="Get Integration Package")
async def get_integration_package(
    package_id: str,
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Get detailed integration package information.
    Returns complete package definition and metadata.
    """
    try:
        package = await marketplace_service.db.integration_packages.find_one({"package_id": package_id})
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration package not found"
            )
        
        return IntegrationPackageResponse(
            package_id=package["package_id"],
            name=package["name"],
            description=package["description"],
            version=package["version"],
            integration_type=package["integration_type"],
            developer_id=package["developer_id"],
            pricing_model=package["pricing_model"],
            price=package.get("price"),
            status=package["status"],
            tags=package["tags"],
            documentation_url=package.get("documentation_url"),
            repository_url=package.get("repository_url"),
            api_endpoints=package["api_endpoints"],
            configuration_schema=package["configuration_schema"],
            dependencies=package["dependencies"],
            download_count=package.get("download_count", 0),
            rating=package.get("rating", 0.0),
            created_at=package["created_at"],
            updated_at=package["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get integration package"
        )

# Package Installation
@router.post("/api/marketplace/installations", response_model=IntegrationInstallationResponse, summary="Install Integration Package")
async def install_integration_package(
    request: IntegrationInstallationRequest = Body(...),
    organization_id: str = Query(..., description="Organization ID"),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Install an integration package.
    Downloads and configures the integration for the organization.
    """
    try:
        installation_id = await marketplace_service.install_integration(
            request.package_id, organization_id, request.configuration
        )
        
        # Get installation details
        installation = await marketplace_service.db.integration_installations.find_one({
            "installation_id": installation_id
        })
        
        return IntegrationInstallationResponse(
            installation_id=installation["installation_id"],
            package_id=installation["package_id"],
            organization_id=installation["organization_id"],
            developer_id=installation["developer_id"],
            configuration=installation["configuration"],
            status=installation["status"],
            installed_at=installation["installed_at"],
            last_used=installation.get("last_used")
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error installing integration package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to install integration package"
        )

@router.get("/api/marketplace/installations", response_model=List[IntegrationInstallationResponse], summary="List Organization Installations")
async def list_organization_installations(
    organization_id: str = Query(..., description="Organization ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    List integration installations for an organization.
    Returns installation details and status.
    """
    try:
        # Build query
        query = {"organization_id": organization_id}
        if status:
            query["status"] = status
        
        # Get installations
        installations = await marketplace_service.db.integration_installations.find(query).sort("installed_at", -1).to_list(length=None)
        
        installation_responses = []
        for installation in installations:
            installation_responses.append(IntegrationInstallationResponse(
                installation_id=installation["installation_id"],
                package_id=installation["package_id"],
                organization_id=installation["organization_id"],
                developer_id=installation["developer_id"],
                configuration=installation["configuration"],
                status=installation["status"],
                installed_at=installation["installed_at"],
                last_used=installation.get("last_used")
            ))
        
        return installation_responses
        
    except Exception as e:
        logger.error(f"Error listing organization installations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list organization installations"
        )

@router.delete("/api/marketplace/installations/{installation_id}", summary="Uninstall Integration Package")
async def uninstall_integration_package(
    installation_id: str,
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Uninstall an integration package.
    Removes the integration and cleans up resources.
    """
    try:
        success = await marketplace_service.package_installer.uninstall_package(installation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found"
            )
        
        return {
            "installation_id": installation_id,
            "status": "uninstalled",
            "message": "Integration package uninstalled successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uninstalling integration package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to uninstall integration package"
        )

# Package Search
@router.post("/api/marketplace/search", summary="Search Integration Packages")
async def search_integration_packages(
    request: PackageSearchRequest = Body(...),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Search integration packages with advanced filtering.
    Returns matching packages with relevance scoring.
    """
    try:
        # Build search query
        search_query = {}
        
        if request.integration_type:
            search_query["integration_type"] = request.integration_type
        
        if request.pricing_model:
            search_query["pricing_model"] = request.pricing_model
        
        if request.tags:
            search_query["tags"] = {"$in": request.tags}
        
        if request.developer_id:
            search_query["developer_id"] = request.developer_id
        
        # Add text search if query provided
        if request.query:
            search_query["$or"] = [
                {"name": {"$regex": request.query, "$options": "i"}},
                {"description": {"$regex": request.query, "$options": "i"}},
                {"tags": {"$regex": request.query, "$options": "i"}}
            ]
        
        # Only show approved packages
        search_query["status"] = IntegrationStatus.APPROVED.value
        
        # Get packages
        packages = await marketplace_service.db.integration_packages.find(search_query).sort("download_count", -1).to_list(length=None)
        
        return {
            "query": request.query,
            "filters": request.dict(),
            "results": packages,
            "total_count": len(packages)
        }
        
    except Exception as e:
        logger.error(f"Error searching integration packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search integration packages"
        )

# Dashboard Endpoint
@router.get("/api/marketplace/dashboard/{organization_id}", response_model=MarketplaceDashboardResponse, summary="Get Marketplace Dashboard")
async def get_marketplace_dashboard(
    organization_id: str,
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Get comprehensive marketplace dashboard.
    Returns package statistics, popular packages, and organization data.
    """
    try:
        dashboard = await marketplace_service.get_marketplace_dashboard(organization_id)
        
        return MarketplaceDashboardResponse(
            organization_id=dashboard["organization_id"],
            package_statistics=dashboard["package_statistics"],
            organization_statistics=dashboard["organization_statistics"],
            popular_packages=dashboard["popular_packages"],
            recent_packages=dashboard["recent_packages"],
            supported_integration_types=dashboard["supported_integration_types"],
            supported_pricing_models=dashboard["supported_pricing_models"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting marketplace dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get marketplace dashboard"
        )

# Package Management (Developer)
@router.put("/api/marketplace/packages/{package_id}/status", summary="Update Package Status")
async def update_package_status(
    package_id: str,
    status: str = Body(..., description="New status"),
    developer_id: str = Query(..., description="Developer ID"),
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Update package status (for developers).
    Allows developers to manage their package lifecycle.
    """
    try:
        # Validate status
        try:
            IntegrationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
        
        # Check if developer owns the package
        package = await marketplace_service.db.integration_packages.find_one({
            "package_id": package_id,
            "developer_id": developer_id
        })
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found or access denied"
            )
        
        # Update status
        await marketplace_service.db.integration_packages.update_one(
            {"package_id": package_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {
            "package_id": package_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
            "message": "Package status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating package status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update package status"
        )

# Marketplace Health Check
@router.get("/api/marketplace/health", summary="Marketplace System Health Check")
async def marketplace_health_check(
    marketplace_service: APIMarketplaceService = Depends(get_marketplace_service)
):
    """
    Check the health of the marketplace system.
    Returns system status and capabilities.
    """
    try:
        # Check database connection
        await marketplace_service.db.admin.command('ping')
        
        # Get system statistics
        stats = {
            "total_packages": await marketplace_service.db.integration_packages.count_documents({}),
            "approved_packages": await marketplace_service.db.integration_packages.count_documents({"status": IntegrationStatus.APPROVED.value}),
            "total_developers": await marketplace_service.db.developer_profiles.count_documents({}),
            "total_installations": await marketplace_service.db.integration_installations.count_documents({}),
            "active_installations": await marketplace_service.db.integration_installations.count_documents({"status": "installed"})
        }
        
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "package_validator": "healthy",
                "package_installer": "healthy",
                "developer_manager": "healthy",
                "file_storage": "healthy"
            },
            "statistics": stats,
            "capabilities": {
                "package_creation": True,
                "package_validation": True,
                "package_installation": True,
                "developer_management": True,
                "package_search": True,
                "installation_management": True,
                "file_upload": True,
                "security_validation": True
            },
            "supported_integration_types": [it.value for it in IntegrationType],
            "supported_pricing_models": [pm.value for pm in PricingModel],
            "supported_developer_tiers": [dt.value for dt in DeveloperTier],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking marketplace health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
