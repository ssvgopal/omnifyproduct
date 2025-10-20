"""
API Marketplace System
Production-grade marketplace for third-party integrations, extensions, and developer ecosystem
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
import hmac
import base64
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
import redis
import jwt
from cryptography.fernet import Fernet
import zipfile
import tempfile
import shutil
import os
import subprocess
import importlib.util

logger = logging.getLogger(__name__)

class IntegrationType(str, Enum):
    """Integration types"""
    WEBHOOK = "webhook"
    API_CLIENT = "api_client"
    DATA_SOURCE = "data_source"
    WORKFLOW_ACTION = "workflow_action"
    CUSTOM_WIDGET = "custom_widget"
    REPORT_TEMPLATE = "report_template"
    AI_MODEL = "ai_model"
    AUTOMATION_RULE = "automation_rule"

class IntegrationStatus(str, Enum):
    """Integration status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"

class PricingModel(str, Enum):
    """Pricing models"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    FREEMIUM = "freemium"

class DeveloperTier(str, Enum):
    """Developer tiers"""
    INDIVIDUAL = "individual"
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    PARTNER = "partner"

@dataclass
class IntegrationPackage:
    """Integration package definition"""
    package_id: str
    name: str
    description: str
    version: str
    integration_type: IntegrationType
    developer_id: str
    pricing_model: PricingModel
    price: Optional[float]
    status: IntegrationStatus
    tags: List[str]
    documentation_url: Optional[str]
    repository_url: Optional[str]
    api_endpoints: List[Dict[str, Any]]
    configuration_schema: Dict[str, Any]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class DeveloperProfile:
    """Developer profile"""
    developer_id: str
    name: str
    email: str
    company: Optional[str]
    tier: DeveloperTier
    api_key: str
    webhook_secret: str
    integrations_count: int
    total_downloads: int
    rating: float
    verified: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class IntegrationInstallation:
    """Integration installation"""
    installation_id: str
    package_id: str
    organization_id: str
    developer_id: str
    configuration: Dict[str, Any]
    status: str
    installed_at: datetime
    last_used: Optional[datetime]

class PackageValidator:
    """Validates integration packages"""
    
    def __init__(self):
        self.validation_rules = {
            IntegrationType.WEBHOOK: self._validate_webhook,
            IntegrationType.API_CLIENT: self._validate_api_client,
            IntegrationType.DATA_SOURCE: self._validate_data_source,
            IntegrationType.WORKFLOW_ACTION: self._validate_workflow_action,
            IntegrationType.CUSTOM_WIDGET: self._validate_custom_widget,
            IntegrationType.REPORT_TEMPLATE: self._validate_report_template,
            IntegrationType.AI_MODEL: self._validate_ai_model,
            IntegrationType.AUTOMATION_RULE: self._validate_automation_rule
        }
    
    async def validate_package(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate integration package"""
        try:
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "metadata": {}
            }
            
            # Basic validation
            basic_validation = await self._validate_basic_structure(package_data)
            validation_results["errors"].extend(basic_validation["errors"])
            validation_results["warnings"].extend(basic_validation["warnings"])
            
            if not basic_validation["valid"]:
                validation_results["valid"] = False
                return validation_results
            
            # Type-specific validation
            integration_type = IntegrationType(package_data["integration_type"])
            if integration_type in self.validation_rules:
                type_validation = await self.validation_rules[integration_type](package_data, package_files)
                validation_results["errors"].extend(type_validation["errors"])
                validation_results["warnings"].extend(type_validation["warnings"])
                validation_results["metadata"].update(type_validation["metadata"])
            
            # Security validation
            security_validation = await self._validate_security(package_data, package_files)
            validation_results["errors"].extend(security_validation["errors"])
            validation_results["warnings"].extend(security_validation["warnings"])
            
            if validation_results["errors"]:
                validation_results["valid"] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating package: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "metadata": {}
            }
    
    async def _validate_basic_structure(self, package_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic package structure"""
        errors = []
        warnings = []
        
        required_fields = ["name", "description", "version", "integration_type", "developer_id"]
        for field in required_fields:
            if field not in package_data or not package_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate version format
        if "version" in package_data:
            version = package_data["version"]
            if not self._is_valid_version(version):
                errors.append(f"Invalid version format: {version}")
        
        # Validate integration type
        if "integration_type" in package_data:
            try:
                IntegrationType(package_data["integration_type"])
            except ValueError:
                errors.append(f"Invalid integration type: {package_data['integration_type']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _validate_webhook(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate webhook integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for webhook endpoint configuration
        if "webhook_endpoints" not in package_data:
            errors.append("Webhook integration must define webhook_endpoints")
        else:
            webhook_endpoints = package_data["webhook_endpoints"]
            if not isinstance(webhook_endpoints, list) or len(webhook_endpoints) == 0:
                errors.append("Webhook integration must have at least one webhook endpoint")
            else:
                metadata["webhook_count"] = len(webhook_endpoints)
        
        # Check for webhook security
        if "webhook_security" not in package_data:
            warnings.append("Webhook integration should define security measures")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_api_client(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate API client integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for API configuration
        if "api_config" not in package_data:
            errors.append("API client integration must define api_config")
        else:
            api_config = package_data["api_config"]
            if "base_url" not in api_config:
                errors.append("API client must define base_url")
            if "authentication" not in api_config:
                errors.append("API client must define authentication method")
        
        # Check for API endpoints
        if "api_endpoints" not in package_data:
            errors.append("API client integration must define api_endpoints")
        else:
            api_endpoints = package_data["api_endpoints"]
            if not isinstance(api_endpoints, list) or len(api_endpoints) == 0:
                errors.append("API client must have at least one API endpoint")
            else:
                metadata["endpoint_count"] = len(api_endpoints)
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_data_source(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate data source integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for data schema
        if "data_schema" not in package_data:
            errors.append("Data source integration must define data_schema")
        else:
            data_schema = package_data["data_schema"]
            if "fields" not in data_schema:
                errors.append("Data schema must define fields")
            else:
                metadata["field_count"] = len(data_schema["fields"])
        
        # Check for data refresh configuration
        if "refresh_config" not in package_data:
            warnings.append("Data source should define refresh configuration")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_workflow_action(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate workflow action integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for action definition
        if "action_definition" not in package_data:
            errors.append("Workflow action integration must define action_definition")
        else:
            action_def = package_data["action_definition"]
            if "name" not in action_def:
                errors.append("Action definition must have a name")
            if "parameters" not in action_def:
                errors.append("Action definition must define parameters")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_custom_widget(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate custom widget integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for widget configuration
        if "widget_config" not in package_data:
            errors.append("Custom widget integration must define widget_config")
        else:
            widget_config = package_data["widget_config"]
            if "component_name" not in widget_config:
                errors.append("Widget config must define component_name")
            if "props" not in widget_config:
                errors.append("Widget config must define props")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_report_template(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate report template integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for template definition
        if "template_definition" not in package_data:
            errors.append("Report template integration must define template_definition")
        else:
            template_def = package_data["template_definition"]
            if "charts" not in template_def:
                errors.append("Template definition must define charts")
            else:
                metadata["chart_count"] = len(template_def["charts"])
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_ai_model(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate AI model integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for model configuration
        if "model_config" not in package_data:
            errors.append("AI model integration must define model_config")
        else:
            model_config = package_data["model_config"]
            if "model_type" not in model_config:
                errors.append("Model config must define model_type")
            if "input_schema" not in model_config:
                errors.append("Model config must define input_schema")
            if "output_schema" not in model_config:
                errors.append("Model config must define output_schema")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_automation_rule(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate automation rule integration"""
        errors = []
        warnings = []
        metadata = {}
        
        # Check for rule definition
        if "rule_definition" not in package_data:
            errors.append("Automation rule integration must define rule_definition")
        else:
            rule_def = package_data["rule_definition"]
            if "conditions" not in rule_def:
                errors.append("Rule definition must define conditions")
            if "actions" not in rule_def:
                errors.append("Rule definition must define actions")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    async def _validate_security(self, package_data: Dict[str, Any], package_files: bytes) -> Dict[str, Any]:
        """Validate package security"""
        errors = []
        warnings = []
        
        # Check for sensitive data
        sensitive_fields = ["password", "secret", "key", "token"]
        package_str = json.dumps(package_data, default=str).lower()
        
        for field in sensitive_fields:
            if field in package_str:
                warnings.append(f"Package may contain sensitive data: {field}")
        
        # Check for external dependencies
        if "dependencies" in package_data:
            dependencies = package_data["dependencies"]
            for dep in dependencies:
                if "http://" in dep.lower():
                    warnings.append(f"Insecure dependency URL: {dep}")
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string is valid"""
        try:
            parts = version.split(".")
            if len(parts) != 3:
                return False
            
            for part in parts:
                int(part)
            
            return True
        except ValueError:
            return False

class PackageInstaller:
    """Handles package installation and management"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.install_path = "/tmp/integrations"
        self._ensure_install_path()
    
    def _ensure_install_path(self):
        """Ensure installation path exists"""
        try:
            os.makedirs(self.install_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating install path: {e}")
    
    async def install_package(self, package_id: str, organization_id: str, configuration: Dict[str, Any]) -> str:
        """Install integration package"""
        try:
            installation_id = str(uuid.uuid4())
            
            # Get package
            package = await self.db.integration_packages.find_one({"package_id": package_id})
            if not package:
                raise ValueError(f"Package {package_id} not found")
            
            # Create installation record
            installation = IntegrationInstallation(
                installation_id=installation_id,
                package_id=package_id,
                organization_id=organization_id,
                developer_id=package["developer_id"],
                configuration=configuration,
                status="installing",
                installed_at=datetime.utcnow(),
                last_used=None
            )
            
            installation_doc = {
                "installation_id": installation_id,
                "package_id": package_id,
                "organization_id": organization_id,
                "developer_id": package["developer_id"],
                "configuration": configuration,
                "status": "installing",
                "installed_at": installation.installed_at.isoformat(),
                "last_used": None
            }
            
            await self.db.integration_installations.insert_one(installation_doc)
            
            # Install package files
            await self._install_package_files(package_id, installation_id)
            
            # Update installation status
            await self.db.integration_installations.update_one(
                {"installation_id": installation_id},
                {"$set": {"status": "installed"}}
            )
            
            logger.info(f"Installed package {package_id} for organization {organization_id}")
            return installation_id
            
        except Exception as e:
            logger.error(f"Error installing package: {e}")
            raise
    
    async def _install_package_files(self, package_id: str, installation_id: str):
        """Install package files to filesystem"""
        try:
            # Get package files
            package_files = await self.db.package_files.find_one({"package_id": package_id})
            if not package_files:
                raise ValueError(f"Package files not found for {package_id}")
            
            # Create installation directory
            install_dir = os.path.join(self.install_path, installation_id)
            os.makedirs(install_dir, exist_ok=True)
            
            # Extract package files
            package_data = package_files["file_data"]
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(package_data)
                temp_file_path = temp_file.name
            
            # Extract ZIP file
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            logger.info(f"Installed package files for {package_id}")
            
        except Exception as e:
            logger.error(f"Error installing package files: {e}")
            raise
    
    async def uninstall_package(self, installation_id: str) -> bool:
        """Uninstall integration package"""
        try:
            # Get installation
            installation = await self.db.integration_installations.find_one({"installation_id": installation_id})
            if not installation:
                raise ValueError(f"Installation {installation_id} not found")
            
            # Remove package files
            install_dir = os.path.join(self.install_path, installation_id)
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            
            # Update installation status
            await self.db.integration_installations.update_one(
                {"installation_id": installation_id},
                {"$set": {"status": "uninstalled"}}
            )
            
            logger.info(f"Uninstalled package {installation['package_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error uninstalling package: {e}")
            raise
    
    async def get_installation_status(self, installation_id: str) -> Dict[str, Any]:
        """Get installation status"""
        try:
            installation = await self.db.integration_installations.find_one({"installation_id": installation_id})
            if not installation:
                raise ValueError(f"Installation {installation_id} not found")
            
            return {
                "installation_id": installation_id,
                "status": installation["status"],
                "installed_at": installation["installed_at"],
                "last_used": installation.get("last_used"),
                "package_id": installation["package_id"],
                "organization_id": installation["organization_id"]
            }
            
        except Exception as e:
            logger.error(f"Error getting installation status: {e}")
            raise

class DeveloperManager:
    """Manages developer accounts and profiles"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    async def create_developer_profile(self, developer_data: Dict[str, Any]) -> str:
        """Create developer profile"""
        try:
            developer_id = str(uuid.uuid4())
            
            # Generate API key and webhook secret
            api_key = self._generate_api_key()
            webhook_secret = self._generate_webhook_secret()
            
            # Encrypt sensitive data
            encrypted_email = self.cipher_suite.encrypt(developer_data["email"].encode()).decode()
            
            developer = DeveloperProfile(
                developer_id=developer_id,
                name=developer_data["name"],
                email=developer_data["email"],
                company=developer_data.get("company"),
                tier=DeveloperTier(developer_data.get("tier", "individual")),
                api_key=api_key,
                webhook_secret=webhook_secret,
                integrations_count=0,
                total_downloads=0,
                rating=0.0,
                verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            developer_doc = {
                "developer_id": developer_id,
                "name": developer.name,
                "email": encrypted_email,
                "company": developer.company,
                "tier": developer.tier.value,
                "api_key": developer.api_key,
                "webhook_secret": developer.webhook_secret,
                "integrations_count": developer.integrations_count,
                "total_downloads": developer.total_downloads,
                "rating": developer.rating,
                "verified": developer.verified,
                "created_at": developer.created_at.isoformat(),
                "updated_at": developer.updated_at.isoformat()
            }
            
            await self.db.developer_profiles.insert_one(developer_doc)
            
            logger.info(f"Created developer profile {developer_id}: {developer.name}")
            return developer_id
            
        except Exception as e:
            logger.error(f"Error creating developer profile: {e}")
            raise
    
    async def get_developer_profile(self, developer_id: str) -> Optional[Dict[str, Any]]:
        """Get developer profile"""
        try:
            developer_doc = await self.db.developer_profiles.find_one({"developer_id": developer_id})
            if not developer_doc:
                return None
            
            # Decrypt email
            encrypted_email = developer_doc["email"]
            decrypted_email = self.cipher_suite.decrypt(encrypted_email.encode()).decode()
            developer_doc["email"] = decrypted_email
            
            return developer_doc
            
        except Exception as e:
            logger.error(f"Error getting developer profile: {e}")
            return None
    
    async def update_developer_profile(self, developer_id: str, updates: Dict[str, Any]) -> bool:
        """Update developer profile"""
        try:
            # Encrypt email if provided
            if "email" in updates:
                encrypted_email = self.cipher_suite.encrypt(updates["email"].encode()).decode()
                updates["email"] = encrypted_email
            
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db.developer_profiles.update_one(
                {"developer_id": developer_id},
                {"$set": updates}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating developer profile: {e}")
            raise
    
    def _generate_api_key(self) -> str:
        """Generate API key"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    def _generate_webhook_secret(self) -> str:
        """Generate webhook secret"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

class APIMarketplaceService:
    """Main service for API marketplace"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.package_validator = PackageValidator()
        self.package_installer = PackageInstaller(db, redis_client)
        self.developer_manager = DeveloperManager(db, redis_client)
    
    async def create_integration_package(self, package_data: Dict[str, Any], package_files: bytes, developer_id: str) -> str:
        """Create integration package"""
        try:
            package_id = str(uuid.uuid4())
            
            # Validate package
            validation_result = await self.package_validator.validate_package(package_data, package_files)
            if not validation_result["valid"]:
                raise ValueError(f"Package validation failed: {validation_result['errors']}")
            
            # Create package
            package = IntegrationPackage(
                package_id=package_id,
                name=package_data["name"],
                description=package_data["description"],
                version=package_data["version"],
                integration_type=IntegrationType(package_data["integration_type"]),
                developer_id=developer_id,
                pricing_model=PricingModel(package_data.get("pricing_model", "free")),
                price=package_data.get("price"),
                status=IntegrationStatus.DRAFT,
                tags=package_data.get("tags", []),
                documentation_url=package_data.get("documentation_url"),
                repository_url=package_data.get("repository_url"),
                api_endpoints=package_data.get("api_endpoints", []),
                configuration_schema=package_data.get("configuration_schema", {}),
                dependencies=package_data.get("dependencies", []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            package_doc = {
                "package_id": package_id,
                "name": package.name,
                "description": package.description,
                "version": package.version,
                "integration_type": package.integration_type.value,
                "developer_id": developer_id,
                "pricing_model": package.pricing_model.value,
                "price": package.price,
                "status": package.status.value,
                "tags": package.tags,
                "documentation_url": package.documentation_url,
                "repository_url": package.repository_url,
                "api_endpoints": package.api_endpoints,
                "configuration_schema": package.configuration_schema,
                "dependencies": package.dependencies,
                "created_at": package.created_at.isoformat(),
                "updated_at": package.updated_at.isoformat(),
                "validation_metadata": validation_result["metadata"]
            }
            
            await self.db.integration_packages.insert_one(package_doc)
            
            # Store package files
            await self.db.package_files.insert_one({
                "package_id": package_id,
                "file_data": package_files,
                "file_size": len(package_files),
                "uploaded_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Created integration package {package_id}: {package.name}")
            return package_id
            
        except Exception as e:
            logger.error(f"Error creating integration package: {e}")
            raise
    
    async def get_integration_packages(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get integration packages with filtering"""
        try:
            query = {}
            
            if filters:
                if filters.get("integration_type"):
                    query["integration_type"] = filters["integration_type"]
                if filters.get("status"):
                    query["status"] = filters["status"]
                if filters.get("pricing_model"):
                    query["pricing_model"] = filters["pricing_model"]
                if filters.get("tags"):
                    query["tags"] = {"$in": filters["tags"]}
                if filters.get("developer_id"):
                    query["developer_id"] = filters["developer_id"]
            
            packages = await self.db.integration_packages.find(query).sort("created_at", -1).to_list(length=None)
            
            return packages
            
        except Exception as e:
            logger.error(f"Error getting integration packages: {e}")
            raise
    
    async def install_integration(self, package_id: str, organization_id: str, configuration: Dict[str, Any]) -> str:
        """Install integration package"""
        try:
            # Check if package exists and is approved
            package = await self.db.integration_packages.find_one({"package_id": package_id})
            if not package:
                raise ValueError(f"Package {package_id} not found")
            
            if package["status"] != IntegrationStatus.APPROVED.value:
                raise ValueError(f"Package {package_id} is not approved for installation")
            
            # Install package
            installation_id = await self.package_installer.install_package(
                package_id, organization_id, configuration
            )
            
            # Update package download count
            await self.db.integration_packages.update_one(
                {"package_id": package_id},
                {"$inc": {"download_count": 1}}
            )
            
            # Update developer download count
            await self.db.developer_profiles.update_one(
                {"developer_id": package["developer_id"]},
                {"$inc": {"total_downloads": 1}}
            )
            
            logger.info(f"Installed integration {package_id} for organization {organization_id}")
            return installation_id
            
        except Exception as e:
            logger.error(f"Error installing integration: {e}")
            raise
    
    async def get_marketplace_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get marketplace dashboard"""
        try:
            # Get package statistics
            total_packages = await self.db.integration_packages.count_documents({})
            approved_packages = await self.db.integration_packages.count_documents({"status": IntegrationStatus.APPROVED.value})
            free_packages = await self.db.integration_packages.count_documents({"pricing_model": PricingModel.FREE.value})
            
            # Get organization installations
            organization_installations = await self.db.integration_installations.find({
                "organization_id": organization_id
            }).to_list(length=None)
            
            # Get popular packages
            popular_packages = await self.db.integration_packages.find({
                "status": IntegrationStatus.APPROVED.value
            }).sort("download_count", -1).limit(10).to_list(length=None)
            
            # Get recent packages
            recent_packages = await self.db.integration_packages.find({
                "status": IntegrationStatus.APPROVED.value
            }).sort("created_at", -1).limit(10).to_list(length=None)
            
            return {
                "organization_id": organization_id,
                "package_statistics": {
                    "total_packages": total_packages,
                    "approved_packages": approved_packages,
                    "free_packages": free_packages,
                    "paid_packages": total_packages - free_packages
                },
                "organization_statistics": {
                    "installed_packages": len(organization_installations),
                    "active_installations": len([i for i in organization_installations if i["status"] == "installed"])
                },
                "popular_packages": popular_packages,
                "recent_packages": recent_packages,
                "supported_integration_types": [it.value for it in IntegrationType],
                "supported_pricing_models": [pm.value for pm in PricingModel],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting marketplace dashboard: {e}")
            raise

# Global instance
api_marketplace_service = None

def get_api_marketplace_service(db: AsyncIOMotorClient, redis_client: redis.Redis) -> APIMarketplaceService:
    """Get API marketplace service instance"""
    global api_marketplace_service
    if api_marketplace_service is None:
        api_marketplace_service = APIMarketplaceService(db, redis_client)
    return api_marketplace_service
