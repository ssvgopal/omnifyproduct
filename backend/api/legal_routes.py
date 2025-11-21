"""
Legal Document API Routes
Endpoints for serving Terms of Service, Privacy Policy, and tracking user acceptance
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse

from models.legal_models import (
    LegalDocument,
    UserLegalAcceptance,
    LegalDocumentResponse,
    AcceptLegalDocumentRequest,
    DocumentType
)
from database.mongodb_schema import MongoDBSchema
from services.oidc_auth import get_current_user, TokenValidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/legal", tags=["Legal"])

# Path to legal documents
LEGAL_DOCS_PATH = Path(__file__).parent.parent.parent / "docs" / "legal"


def get_legal_document_path(document_type: DocumentType) -> Path:
    """Get file path for legal document"""
    filename_map = {
        DocumentType.TERMS_OF_SERVICE: "terms-of-service.md",
        DocumentType.PRIVACY_POLICY: "privacy-policy.md",
        DocumentType.COOKIE_POLICY: "cookie-policy.md",
        DocumentType.ACCEPTABLE_USE_POLICY: "acceptable-use-policy.md",
        DocumentType.SERVICE_LEVEL_AGREEMENT: "service-level-agreement.md",
    }
    filename = filename_map.get(document_type, f"{document_type.value}.md")
    return LEGAL_DOCS_PATH / filename


@router.get("/terms", response_model=LegalDocumentResponse)
async def get_terms_of_service():
    """Get current Terms of Service"""
    try:
        doc_path = get_legal_document_path(DocumentType.TERMS_OF_SERVICE)
        
        if not doc_path.exists():
            logger.warning(f"Terms of Service not found at {doc_path}")
            # Return a placeholder if file doesn't exist
            return LegalDocumentResponse(
                document_type="terms_of_service",
                version="1.0",
                effective_date=datetime.utcnow().isoformat(),
                content="# Terms of Service\n\n*Document pending. Please contact support.*",
                acceptance_required=True
            )
        
        content = doc_path.read_text(encoding="utf-8")
        
        return LegalDocumentResponse(
            document_type="terms_of_service",
            version="1.0",
            effective_date=datetime.utcnow().isoformat(),
            content=content,
            acceptance_required=True
        )
    except Exception as e:
        logger.error(f"Error loading Terms of Service: {e}")
        raise HTTPException(status_code=500, detail="Failed to load Terms of Service")


@router.get("/privacy", response_model=LegalDocumentResponse)
async def get_privacy_policy():
    """Get current Privacy Policy"""
    try:
        doc_path = get_legal_document_path(DocumentType.PRIVACY_POLICY)
        
        if not doc_path.exists():
            logger.warning(f"Privacy Policy not found at {doc_path}")
            return LegalDocumentResponse(
                document_type="privacy_policy",
                version="1.0",
                effective_date=datetime.utcnow().isoformat(),
                content="# Privacy Policy\n\n*Document pending. Please contact support.*",
                acceptance_required=True
            )
        
        content = doc_path.read_text(encoding="utf-8")
        
        return LegalDocumentResponse(
            document_type="privacy_policy",
            version="1.0",
            effective_date=datetime.utcnow().isoformat(),
            content=content,
            acceptance_required=True
        )
    except Exception as e:
        logger.error(f"Error loading Privacy Policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to load Privacy Policy")


@router.get("/cookie", response_model=LegalDocumentResponse)
async def get_cookie_policy():
    """Get Cookie Policy"""
    try:
        doc_path = get_legal_document_path(DocumentType.COOKIE_POLICY)
        
        if not doc_path.exists():
            return LegalDocumentResponse(
                document_type="cookie_policy",
                version="1.0",
                effective_date=datetime.utcnow().isoformat(),
                content="# Cookie Policy\n\n*Document pending.*",
                acceptance_required=False
            )
        
        content = doc_path.read_text(encoding="utf-8")
        
        return LegalDocumentResponse(
            document_type="cookie_policy",
            version="1.0",
            effective_date=datetime.utcnow().isoformat(),
            content=content,
            acceptance_required=False
        )
    except Exception as e:
        logger.error(f"Error loading Cookie Policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to load Cookie Policy")


@router.post("/accept")
async def accept_legal_document(
    request: AcceptLegalDocumentRequest,
    http_request: Request,
    current_user: Optional[TokenValidationResult] = Depends(get_current_user)
):
    """
    Record user acceptance of legal documents
    
    Note: For beta, we allow unauthenticated acceptance (tracked by IP/user agent)
    """
    try:
        db = MongoDBSchema()
        
        # Get user info if authenticated, otherwise use anonymous
        user_id = current_user.user_id if current_user else "anonymous"
        organization_id = current_user.organization_id if current_user else None
        
        # Get IP and user agent
        ip_address = request.ip_address or http_request.client.host if http_request.client else None
        user_agent = request.user_agent or http_request.headers.get("user-agent")
        
        acceptance = UserLegalAcceptance(
            user_id=user_id,
            organization_id=organization_id,
            document_id=request.document_id,
            document_type=request.document_type,
            version=request.version,
            accepted_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store in database
        result = await db.user_legal_acceptances.insert_one(acceptance.dict())
        
        logger.info(f"Legal document acceptance recorded: {user_id} accepted {request.document_type} v{request.version}")
        
        return {
            "status": "accepted",
            "acceptance_id": str(result.inserted_id),
            "document_type": request.document_type,
            "version": request.version,
            "accepted_at": acceptance.accepted_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error recording legal acceptance: {e}")
        raise HTTPException(status_code=500, detail="Failed to record acceptance")


@router.get("/acceptances")
async def get_user_acceptances(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get all legal document acceptances for current user"""
    try:
        db = MongoDBSchema()
        
        acceptances = await db.user_legal_acceptances.find(
            {"user_id": current_user.user_id}
        ).to_list(length=100)
        
        return {
            "acceptances": acceptances,
            "count": len(acceptances)
        }
    except Exception as e:
        logger.error(f"Error fetching acceptances: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch acceptances")

