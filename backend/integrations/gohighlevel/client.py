"""
Production-Ready GoHighLevel API Integration for OmnifyProduct
Complete GoHighLevel CRM and marketing automation integration

Features:
- OAuth2 authentication flow
- Contact management and synchronization
- Workflow automation triggers
- Campaign management integration
- Opportunity and pipeline tracking
- Email and SMS automation
- Calendar and appointment booking
- Comprehensive API coverage
"""

import os
import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

class GoHighLevelIntegration:
    """
    Complete GoHighLevel API integration for agency CRM and marketing automation
    """

    def __init__(self):
        self.client_id = os.environ.get('GOHIGHLEVEL_CLIENT_ID')
        self.client_secret = os.environ.get('GOHIGHLEVEL_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOHIGHLEVEL_REDIRECT_URI', 'http://localhost:8000/auth/gohighlevel/callback')

        # API configuration
        self.base_url = 'https://api.gohighlevel.com'
        self.api_version = 'v1'
        self.timeout_seconds = 30

        # Rate limiting (GoHighLevel has limits)
        self.requests_per_second = 10  # Conservative limit
        self.requests_per_minute = 1000
        self.daily_limit = 50000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes

        # HTTP client
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds
            )

        logger.info("GoHighLevel integration initialized", extra={
            "has_client": HAS_HTTPX and self.client is not None,
            "base_url": self.base_url,
            "rate_limit_per_second": self.requests_per_second
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, state: str, location_id: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL for GoHighLevel
        """
        base_url = "https://marketplace.gohighlevel.com/oauth/chooselocation"
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'locations.readonly contacts.write contacts.readonly workflows.readonly workflows.write campaigns.readonly campaigns.write opportunities.write opportunities.readonly',
            'state': state
        }

        if location_id:
            params['location_id'] = location_id

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access tokens
        """
        try:
            if not self.client:
                return None

            token_url = "/oauth/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

            # Extract company and location info
            access_token = tokens['access_token']
            company_info = await self._get_company_info(access_token)

            tokens.update({
                'company_id': company_info.get('company_id'),
                'location_id': company_info.get('location_id'),
                'location_name': company_info.get('location_name')
            })

            logger.info("GoHighLevel OAuth tokens obtained successfully", extra={
                "company_id": company_info.get('company_id'),
                "location_id": company_info.get('location_id')
            })

            return tokens

        except Exception as e:
            logger.error("Failed to exchange GoHighLevel OAuth code for tokens", exc_info=e)
            return None

    async def _get_company_info(self, access_token: str) -> Dict[str, Any]:
        """Get company and location information from access token"""
        try:
            if not self.client:
                return {}

            # Set authorization header
            headers = {'Authorization': f'Bearer {access_token}'}

            # Get user info (contains company/location data)
            response = await self.client.get('/users/me', headers=headers)
            response.raise_for_status()

            user_data = response.json()

            return {
                'company_id': user_data.get('company_id'),
                'location_id': user_data.get('location_id'),
                'location_name': user_data.get('location_name'),
                'user_id': user_data.get('id'),
                'user_name': user_data.get('name')
            }

        except Exception as e:
            logger.warning("Failed to get GoHighLevel company info", exc_info=e)
            return {}

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh expired access token
        """
        try:
            if not self.client:
                return None

            token_url = "/oauth/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

            logger.info("GoHighLevel access token refreshed")
            return tokens

        except Exception as e:
            logger.error("Failed to refresh GoHighLevel access token", exc_info=e)
            return None

    async def get_valid_access_token(self, organization_id: str, location_id: str) -> Optional[str]:
        """
        Get valid access token for GoHighLevel location
        """
        try:
            # Get stored tokens
            tokens_key = f"gohighlevel_tokens_{organization_id}_{location_id}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Check if token is still valid (with buffer)
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            buffer_time = timedelta(minutes=5)  # Refresh 5 minutes before expiry

            if datetime.utcnow() >= (expires_at - buffer_time):
                # Refresh token
                refreshed = await self.refresh_access_token(tokens['refresh_token'])
                if refreshed:
                    refreshed['refresh_token'] = tokens['refresh_token']  # Keep original refresh token
                    await production_secrets_manager.update_secret(tokens_key, refreshed)
                    tokens = refreshed
                else:
                    logger.warning("Failed to refresh GoHighLevel tokens", extra={
                        "organization_id": organization_id,
                        "location_id": location_id
                    })
                    return None

            return tokens['access_token']

        except Exception as e:
            logger.error("Failed to get valid GoHighLevel access token", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return None

    # ========== LOCATION MANAGEMENT ==========

    async def list_locations(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List accessible GoHighLevel locations
        """
        try:
            # Get access token (try default location first)
            access_token = await self.get_valid_access_token(organization_id, "default")
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            response = await self.client.get('/locations/', headers=headers)
            response.raise_for_status()

            locations_data = response.json()
            locations = locations_data.get('locations', [])

            location_list = []
            for location in locations:
                location_list.append({
                    "location_id": location.get('id'),
                    "name": location.get('name'),
                    "address": location.get('address'),
                    "city": location.get('city'),
                    "state": location.get('state'),
                    "country": location.get('country'),
                    "phone": location.get('phone'),
                    "website": location.get('website'),
                    "timezone": location.get('timezone')
                })

            # Cache results
            cache_key = f"gohighlevel_locations_{organization_id}"
            await production_secrets_manager.store_secret(cache_key, location_list, {"ttl": self.cache_ttl})

            logger.info("GoHighLevel locations retrieved", extra={
                "organization_id": organization_id,
                "location_count": len(location_list)
            })

            return location_list

        except Exception as e:
            logger.error("Failed to list GoHighLevel locations", exc_info=e, extra={
                "organization_id": organization_id
            })
            return []

    # ========== CONTACT MANAGEMENT ==========

    async def create_contact(
        self,
        organization_id: str,
        location_id: str,
        contact_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a new contact in GoHighLevel
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format contact data for GoHighLevel API
            contact_payload = {
                'firstName': contact_data.get('first_name', ''),
                'lastName': contact_data.get('last_name', ''),
                'name': contact_data.get('name', ''),
                'email': contact_data.get('email'),
                'phone': contact_data.get('phone'),
                'address1': contact_data.get('address'),
                'city': contact_data.get('city'),
                'state': contact_data.get('state'),
                'country': contact_data.get('country'),
                'postalCode': contact_data.get('postal_code'),
                'companyName': contact_data.get('company'),
                'website': contact_data.get('website'),
                'tags': contact_data.get('tags', []),
                'customFields': contact_data.get('custom_fields', {})
            }

            # Remove empty fields
            contact_payload = {k: v for k, v in contact_payload.items() if v is not None and v != ''}

            response = await self.client.post(
                f'/contacts/',
                headers=headers,
                json=contact_payload
            )
            response.raise_for_status()

            contact_result = response.json()
            contact_id = contact_result.get('contact', {}).get('id')

            logger.info("GoHighLevel contact created", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "contact_id": contact_id,
                "contact_name": contact_data.get('name')
            })

            return contact_id

        except Exception as e:
            logger.error("Failed to create GoHighLevel contact", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return None

    async def update_contact(
        self,
        organization_id: str,
        location_id: str,
        contact_id: str,
        contact_data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing contact
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return False

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format update data
            update_payload = {
                'firstName': contact_data.get('first_name'),
                'lastName': contact_data.get('last_name'),
                'email': contact_data.get('email'),
                'phone': contact_data.get('phone'),
                'tags': contact_data.get('tags'),
                'customFields': contact_data.get('custom_fields')
            }

            # Remove None values
            update_payload = {k: v for k, v in update_payload.items() if v is not None}

            response = await self.client.put(
                f'/contacts/{contact_id}',
                headers=headers,
                json=update_payload
            )
            response.raise_for_status()

            logger.info("GoHighLevel contact updated", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "contact_id": contact_id
            })

            return True

        except Exception as e:
            logger.error("Failed to update GoHighLevel contact", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "contact_id": contact_id
            })
            return False

    async def get_contacts(
        self,
        organization_id: str,
        location_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve contacts with optional filtering
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            # Build query parameters
            params = {'limit': min(limit, 100)}  # GoHighLevel limit

            if filters:
                if 'email' in filters:
                    params['email'] = filters['email']
                if 'phone' in filters:
                    params['phone'] = filters['phone']
                if 'tags' in filters:
                    params['tags'] = ','.join(filters['tags'])

            response = await self.client.get('/contacts/', headers=headers, params=params)
            response.raise_for_status()

            contacts_data = response.json()
            contacts = contacts_data.get('contacts', [])

            # Format contacts for our system
            formatted_contacts = []
            for contact in contacts:
                formatted_contacts.append({
                    "contact_id": contact.get('id'),
                    "first_name": contact.get('firstName'),
                    "last_name": contact.get('lastName'),
                    "name": contact.get('name'),
                    "email": contact.get('email'),
                    "phone": contact.get('phone'),
                    "company": contact.get('companyName'),
                    "tags": contact.get('tags', []),
                    "created_at": contact.get('createdAt'),
                    "updated_at": contact.get('updatedAt'),
                    "custom_fields": contact.get('customFields', {})
                })

            logger.info("GoHighLevel contacts retrieved", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "contact_count": len(formatted_contacts)
            })

            return formatted_contacts

        except Exception as e:
            logger.error("Failed to get GoHighLevel contacts", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return []

    # ========== WORKFLOW MANAGEMENT ==========

    async def trigger_workflow(
        self,
        organization_id: str,
        location_id: str,
        workflow_id: str,
        contact_id: str,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Trigger a GoHighLevel workflow for a contact
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return False

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'workflowId': workflow_id,
                'contactId': contact_id,
                'triggerData': trigger_data or {}
            }

            response = await self.client.post(
                '/workflows/trigger',
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            logger.info("GoHighLevel workflow triggered", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "workflow_id": workflow_id,
                "contact_id": contact_id
            })

            return True

        except Exception as e:
            logger.error("Failed to trigger GoHighLevel workflow", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "workflow_id": workflow_id,
                "contact_id": contact_id
            })
            return False

    async def list_workflows(self, organization_id: str, location_id: str) -> List[Dict[str, Any]]:
        """
        List available workflows
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            response = await self.client.get('/workflows/', headers=headers)
            response.raise_for_status()

            workflows_data = response.json()
            workflows = workflows_data.get('workflows', [])

            formatted_workflows = []
            for workflow in workflows:
                formatted_workflows.append({
                    "workflow_id": workflow.get('id'),
                    "name": workflow.get('name'),
                    "status": workflow.get('status'),
                    "trigger_type": workflow.get('triggerType'),
                    "created_at": workflow.get('createdAt'),
                    "updated_at": workflow.get('updatedAt')
                })

            logger.info("GoHighLevel workflows retrieved", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "workflow_count": len(formatted_workflows)
            })

            return formatted_workflows

        except Exception as e:
            logger.error("Failed to list GoHighLevel workflows", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return []

    # ========== OPPORTUNITY MANAGEMENT ==========

    async def create_opportunity(
        self,
        organization_id: str,
        location_id: str,
        opportunity_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a new opportunity/pipeline entry
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'name': opportunity_data.get('name'),
                'contactId': opportunity_data.get('contact_id'),
                'pipelineId': opportunity_data.get('pipeline_id'),
                'status': opportunity_data.get('status', 'new'),
                'monetaryValue': opportunity_data.get('value', 0),
                'assignedTo': opportunity_data.get('assigned_to'),
                'customFields': opportunity_data.get('custom_fields', {})
            }

            response = await self.client.post(
                '/opportunities/',
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            opportunity_result = response.json()
            opportunity_id = opportunity_result.get('opportunity', {}).get('id')

            logger.info("GoHighLevel opportunity created", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "opportunity_id": opportunity_id,
                "contact_id": opportunity_data.get('contact_id')
            })

            return opportunity_id

        except Exception as e:
            logger.error("Failed to create GoHighLevel opportunity", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return None

    async def update_opportunity_status(
        self,
        organization_id: str,
        location_id: str,
        opportunity_id: str,
        status: str,
        status_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update opportunity status
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return False

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'status': status,
                **(status_data or {})
            }

            response = await self.client.put(
                f'/opportunities/{opportunity_id}',
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            logger.info("GoHighLevel opportunity status updated", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "opportunity_id": opportunity_id,
                "new_status": status
            })

            return True

        except Exception as e:
            logger.error("Failed to update GoHighLevel opportunity status", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "opportunity_id": opportunity_id
            })
            return False

    # ========== CAMPAIGN MANAGEMENT ==========

    async def create_campaign(
        self,
        organization_id: str,
        location_id: str,
        campaign_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a marketing campaign in GoHighLevel
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'name': campaign_data.get('name'),
                'type': campaign_data.get('type', 'email'),
                'status': campaign_data.get('status', 'draft'),
                'schedule': campaign_data.get('schedule', {}),
                'settings': campaign_data.get('settings', {}),
                'content': campaign_data.get('content', {})
            }

            response = await self.client.post(
                '/campaigns/',
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            campaign_result = response.json()
            campaign_id = campaign_result.get('campaign', {}).get('id')

            logger.info("GoHighLevel campaign created", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "campaign_id": campaign_id,
                "campaign_name": campaign_data.get('name')
            })

            return campaign_id

        except Exception as e:
            logger.error("Failed to create GoHighLevel campaign", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return None

    # ========== CALENDAR & APPOINTMENTS ==========

    async def create_appointment(
        self,
        organization_id: str,
        location_id: str,
        appointment_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Schedule a calendar appointment
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, location_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'calendarId': appointment_data.get('calendar_id'),
                'contactId': appointment_data.get('contact_id'),
                'title': appointment_data.get('title'),
                'startTime': appointment_data.get('start_time'),
                'endTime': appointment_data.get('end_time'),
                'location': appointment_data.get('location'),
                'notes': appointment_data.get('notes'),
                'assignedUserId': appointment_data.get('assigned_user_id')
            }

            response = await self.client.post(
                '/appointments/',
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            appointment_result = response.json()
            appointment_id = appointment_result.get('appointment', {}).get('id')

            logger.info("GoHighLevel appointment created", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "appointment_id": appointment_id,
                "contact_id": appointment_data.get('contact_id')
            })

            return appointment_id

        except Exception as e:
            logger.error("Failed to create GoHighLevel appointment", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return None

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, location_id: str) -> Dict[str, Any]:
        """
        Test connection to GoHighLevel API
        """
        try:
            locations = await self.list_locations(organization_id)
            if locations:
                return {
                    "status": "connected",
                    "locations_count": len(locations),
                    "first_location": locations[0]["location_id"] if locations else None
                }
            else:
                return {"status": "no_locations"}
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def get_required_scopes(self) -> List[str]:
        """Get required OAuth2 scopes"""
        return [
            'locations.readonly',
            'contacts.write',
            'contacts.readonly',
            'workflows.readonly',
            'workflows.write',
            'campaigns.readonly',
            'campaigns.write',
            'opportunities.write',
            'opportunities.readonly'
        ]

    def get_api_limits(self) -> Dict[str, Any]:
        """Get GoHighLevel API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_minute": self.requests_per_minute,
            "daily_limit": self.daily_limit,
            "rate_limit_type": "location_based",
            "burst_allowed": True,
            "plan_based_limits": True,
            "documentation_url": "https://developers.gohighlevel.com/"
        }

    async def sync_contacts_to_omnify(
        self,
        organization_id: str,
        location_id: str,
        last_sync: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Sync GoHighLevel contacts to OmnifyProduct database
        """
        try:
            # Get contacts updated since last sync
            filters = {}
            if last_sync:
                filters['updated_after'] = last_sync.isoformat()

            contacts = await self.get_contacts(organization_id, location_id, filters, limit=1000)

            synced_count = 0
            tenant_manager = get_tenant_manager()

            for contact in contacts:
                # Set tenant context
                tenant_manager.set_tenant_context(organization_id)

                # Check if contact exists in our database
                existing_contact = await tenant_manager.db.clients.find_one({
                    "organization_id": organization_id,
                    "email": contact["email"]
                })

                if existing_contact:
                    # Update existing contact
                    await tenant_manager.db.clients.update_one(
                        {"_id": existing_contact["_id"]},
                        {"$set": {
                            **contact,
                            "updated_at": datetime.utcnow(),
                            "source": "gohighlevel"
                        }}
                    )
                else:
                    # Create new contact
                    contact["organization_id"] = organization_id
                    contact["created_at"] = datetime.utcnow()
                    contact["updated_at"] = datetime.utcnow()
                    contact["source"] = "gohighlevel"

                    await tenant_manager.db.clients.insert_one(contact)

                synced_count += 1

            logger.info("GoHighLevel contacts synced to OmnifyProduct", extra={
                "organization_id": organization_id,
                "location_id": location_id,
                "synced_count": synced_count
            })

            return {
                "status": "completed",
                "synced_contacts": synced_count,
                "last_sync": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Failed to sync GoHighLevel contacts", exc_info=e, extra={
                "organization_id": organization_id,
                "location_id": location_id
            })
            return {
                "status": "error",
                "error": str(e),
                "synced_contacts": 0
            }

# Global GoHighLevel integration instance
gohighlevel_integration = GoHighLevelIntegration()
