"""
Legal Document Models
Models for Terms of Service, Privacy Policy, and user acceptance tracking
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class DocumentType(str, Enum):
    """Types of legal documents"""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    COOKIE_POLICY = "cookie_policy"
    ACCEPTABLE_USE_POLICY = "acceptable_use_policy"
    SERVICE_LEVEL_AGREEMENT = "service_level_agreement"


class LegalDocument(BaseModel):
    """Legal document model"""
    id: str = Field(..., description="Document ID")
    document_type: DocumentType = Field(..., description="Type of document")
    version: str = Field(..., description="Document version (e.g., '1.0')")
    effective_date: datetime = Field(..., description="When this version became effective")
    content: str = Field(..., description="Document content (Markdown)")
    acceptance_required: bool = Field(default=True, description="Whether user acceptance is required")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class UserLegalAcceptance(BaseModel):
    """User acceptance of legal documents"""
    id: Optional[str] = Field(None, description="Acceptance record ID")
    user_id: str = Field(..., description="User ID who accepted")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    document_id: str = Field(..., description="Document ID that was accepted")
    document_type: DocumentType = Field(..., description="Type of document")
    version: str = Field(..., description="Version of document accepted")
    accepted_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None, description="IP address when accepted")
    user_agent: Optional[str] = Field(None, description="User agent when accepted")
    
    class Config:
        use_enum_values = True


class LegalDocumentResponse(BaseModel):
    """Response model for legal document"""
    document_type: str
    version: str
    effective_date: str
    content: str
    acceptance_required: bool


class AcceptLegalDocumentRequest(BaseModel):
    """Request to accept a legal document"""
    document_id: str
    document_type: DocumentType
    version: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        use_enum_values = True

