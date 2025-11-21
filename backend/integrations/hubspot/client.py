"""
HubSpot API Integration
CRM and Marketing Automation platform for mid-market companies

Features:
- CRM contact management
- Marketing automation workflows
- Sales pipeline management
- Campaign creation and management
- Reporting and analytics
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class HubSpotConfig:
    """Configuration for HubSpot API"""
    access_token: str
    base_url: str = "https://api.hubapi.com"
    timeout: int = 30

class HubSpotClient:
    """
    HubSpot API Client
    Integrates with HubSpot CRM and Marketing Automation platform
    """
    
    def __init__(self, config: HubSpotConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to HubSpot API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"HubSpot API error: {response.status} - {response_data}")
                    raise Exception(f"HubSpot API error: {response.status} - {response_data}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"HubSpot API request failed: {e}")
            raise Exception(f"HubSpot API request failed: {e}")
    
    # ========== CONTACT MANAGEMENT METHODS ==========
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contact in HubSpot CRM
        
        Args:
            contact_data: Contact information (email, firstname, lastname, etc.)
        
        Returns:
            Created contact data
        """
        try:
            # HubSpot expects properties in a specific format
            properties = []
            for key, value in contact_data.items():
                properties.append({
                    "property": key,
                    "value": value
                })
            
            data = {"properties": properties}
            
            response = await self._make_request("POST", "/crm/v3/objects/contacts", data=data)
            
            logger.info(f"Created HubSpot contact: {response.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create HubSpot contact: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to create contact - {str(e)}")
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get a contact from HubSpot
        
        Args:
            contact_id: HubSpot contact ID
        
        Returns:
            Contact data
        """
        try:
            response = await self._make_request("GET", f"/crm/v3/objects/contacts/{contact_id}")
            
            logger.info(f"Retrieved HubSpot contact: {contact_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get HubSpot contact: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to get contact - {str(e)}")
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a contact in HubSpot
        
        Args:
            contact_id: HubSpot contact ID
            contact_data: Updated contact information
        
        Returns:
            Updated contact data
        """
        try:
            properties = []
            for key, value in contact_data.items():
                properties.append({
                    "property": key,
                    "value": value
                })
            
            data = {"properties": properties}
            
            response = await self._make_request("PATCH", f"/crm/v3/objects/contacts/{contact_id}", data=data)
            
            logger.info(f"Updated HubSpot contact: {contact_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to update HubSpot contact: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to update contact - {str(e)}")
    
    async def search_contacts(self, query: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Search contacts in HubSpot
        
        Args:
            query: Optional search query
            limit: Maximum number of results
        
        Returns:
            Search results
        """
        try:
            params = {"limit": limit}
            
            if query:
                # HubSpot search API
                data = {
                    "query": query,
                    "limit": limit
                }
                response = await self._make_request("POST", "/crm/v3/objects/contacts/search", data=data)
            else:
                response = await self._make_request("GET", "/crm/v3/objects/contacts", params=params)
            
            logger.info(f"Retrieved HubSpot contacts: {len(response.get('results', []))} results")
            return response
            
        except Exception as e:
            logger.error(f"Failed to search HubSpot contacts: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to search contacts - {str(e)}")
    
    # ========== DEAL/PIPELINE MANAGEMENT METHODS ==========
    
    async def create_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deal in HubSpot
        
        Args:
            deal_data: Deal information (dealname, amount, pipeline, stage, etc.)
        
        Returns:
            Created deal data
        """
        try:
            properties = []
            for key, value in deal_data.items():
                properties.append({
                    "property": key,
                    "value": value
                })
            
            data = {"properties": properties}
            
            response = await self._make_request("POST", "/crm/v3/objects/deals", data=data)
            
            logger.info(f"Created HubSpot deal: {response.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create HubSpot deal: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to create deal - {str(e)}")
    
    async def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """
        Get a deal from HubSpot
        
        Args:
            deal_id: HubSpot deal ID
        
        Returns:
            Deal data
        """
        try:
            response = await self._make_request("GET", f"/crm/v3/objects/deals/{deal_id}")
            
            logger.info(f"Retrieved HubSpot deal: {deal_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get HubSpot deal: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to get deal - {str(e)}")
    
    async def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a deal in HubSpot
        
        Args:
            deal_id: HubSpot deal ID
            deal_data: Updated deal information
        
        Returns:
            Updated deal data
        """
        try:
            properties = []
            for key, value in deal_data.items():
                properties.append({
                    "property": key,
                    "value": value
                })
            
            data = {"properties": properties}
            
            response = await self._make_request("PATCH", f"/crm/v3/objects/deals/{deal_id}", data=data)
            
            logger.info(f"Updated HubSpot deal: {deal_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to update HubSpot deal: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to update deal - {str(e)}")
    
    # ========== MARKETING AUTOMATION METHODS ==========
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a marketing automation workflow
        
        Args:
            workflow_data: Workflow configuration
        
        Returns:
            Created workflow data
        """
        try:
            response = await self._make_request("POST", "/automation/v4/workflows", data=workflow_data)
            
            logger.info(f"Created HubSpot workflow: {response.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create HubSpot workflow: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to create workflow - {str(e)}")
    
    async def trigger_workflow(self, workflow_id: str, contact_id: str) -> Dict[str, Any]:
        """
        Trigger a workflow for a contact
        
        Args:
            workflow_id: HubSpot workflow ID
            contact_id: Contact ID to trigger workflow for
        
        Returns:
            Trigger result
        """
        try:
            data = {
                "contactId": contact_id
            }
            
            response = await self._make_request("POST", f"/automation/v4/workflows/{workflow_id}/enrollments", data=data)
            
            logger.info(f"Triggered HubSpot workflow {workflow_id} for contact {contact_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to trigger HubSpot workflow: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to trigger workflow - {str(e)}")
    
    # ========== CAMPAIGN METHODS ==========
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a marketing campaign
        
        Args:
            campaign_data: Campaign configuration
        
        Returns:
            Created campaign data
        """
        try:
            response = await self._make_request("POST", "/marketing/v3/campaigns", data=campaign_data)
            
            logger.info(f"Created HubSpot campaign: {response.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create HubSpot campaign: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to create campaign - {str(e)}")
    
    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get a campaign from HubSpot
        
        Args:
            campaign_id: HubSpot campaign ID
        
        Returns:
            Campaign data
        """
        try:
            response = await self._make_request("GET", f"/marketing/v3/campaigns/{campaign_id}")
            
            logger.info(f"Retrieved HubSpot campaign: {campaign_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get HubSpot campaign: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to get campaign - {str(e)}")
    
    # ========== ANALYTICS/REPORTING METHODS ==========
    
    async def get_analytics(self, start_date: str, end_date: str, object_type: str = "contacts") -> Dict[str, Any]:
        """
        Get analytics data from HubSpot
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            object_type: Object type (contacts, deals, companies, etc.)
        
        Returns:
            Analytics data
        """
        try:
            params = {
                "startDate": start_date,
                "endDate": end_date
            }
            
            response = await self._make_request("GET", f"/analytics/v3/reports/{object_type}", params=params)
            
            logger.info(f"Retrieved HubSpot analytics: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get HubSpot analytics: {e}", exc_info=True)
            raise RuntimeError(f"HubSpot API error: Failed to get analytics - {str(e)}")

class HubSpotAdapter:
    """HubSpot adapter with unified interface for Omnify"""
    
    def __init__(self):
        self.client: Optional[HubSpotClient] = None
        self.config: Optional[HubSpotConfig] = None
        
    async def initialize(self, config: Dict[Any, Any]):
        """Initialize HubSpot adapter with configuration"""
        access_token = config.get('access_token')
        if not access_token:
            raise ValueError("HubSpot access token is required")
        
        self.config = HubSpotConfig(
            access_token=access_token,
            base_url=config.get('base_url', 'https://api.hubapi.com'),
            timeout=config.get('timeout', 30)
        )
        
        logger.info("HubSpot adapter initialized")
        
    async def create_contact(
        self,
        organization_id: str,
        contact_data: Dict[Any, Any]
    ) -> Dict[Any, Any]:
        """Create a contact in HubSpot CRM"""
        if not self.config:
            raise RuntimeError("HubSpot adapter not initialized")
        
        async with HubSpotClient(self.config) as client:
            try:
                response = await client.create_contact(contact_data)
                
                return {
                    'status': 'success',
                    'contact_id': response.get('id'),
                    'data': response,
                    'platform': 'hubspot',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to create HubSpot contact: {e}", exc_info=True)
                raise RuntimeError(f"HubSpot API error: Failed to create contact - {str(e)}")
    
    async def create_campaign(
        self,
        organization_id: str,
        campaign_data: Dict[Any, Any]
    ) -> Dict[Any, Any]:
        """Create a marketing campaign in HubSpot"""
        if not self.config:
            raise RuntimeError("HubSpot adapter not initialized")
        
        async with HubSpotClient(self.config) as client:
            try:
                response = await client.create_campaign(campaign_data)
                
                return {
                    'status': 'success',
                    'campaign_id': response.get('id'),
                    'data': response,
                    'platform': 'hubspot',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to create HubSpot campaign: {e}", exc_info=True)
                raise RuntimeError(f"HubSpot API error: Failed to create campaign - {str(e)}")
    
    async def create_workflow(
        self,
        organization_id: str,
        workflow_data: Dict[Any, Any]
    ) -> Dict[Any, Any]:
        """Create a marketing automation workflow in HubSpot"""
        if not self.config:
            raise RuntimeError("HubSpot adapter not initialized")
        
        async with HubSpotClient(self.config) as client:
            try:
                response = await client.create_workflow(workflow_data)
                
                return {
                    'status': 'success',
                    'workflow_id': response.get('id'),
                    'data': response,
                    'platform': 'hubspot',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to create HubSpot workflow: {e}", exc_info=True)
                raise RuntimeError(f"HubSpot API error: Failed to create workflow - {str(e)}")
    
    async def trigger_workflow(
        self,
        organization_id: str,
        workflow_id: str,
        contact_id: str
    ) -> Dict[Any, Any]:
        """Trigger a workflow for a contact"""
        if not self.config:
            raise RuntimeError("HubSpot adapter not initialized")
        
        async with HubSpotClient(self.config) as client:
            try:
                response = await client.trigger_workflow(workflow_id, contact_id)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'hubspot',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to trigger HubSpot workflow: {e}", exc_info=True)
                raise RuntimeError(f"HubSpot API error: Failed to trigger workflow - {str(e)}")
    
    async def get_analytics(
        self,
        organization_id: str,
        start_date: str,
        end_date: str,
        object_type: str = "contacts"
    ) -> Dict[Any, Any]:
        """Get analytics data from HubSpot"""
        if not self.config:
            raise RuntimeError("HubSpot adapter not initialized")
        
        async with HubSpotClient(self.config) as client:
            try:
                response = await client.get_analytics(start_date, end_date, object_type)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'hubspot',
                    'organization_id': organization_id,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to get HubSpot analytics: {e}", exc_info=True)
                raise RuntimeError(f"HubSpot API error: Failed to get analytics - {str(e)}")
    
    async def test_connection(self, organization_id: str, account_id: str = "default") -> Dict[str, Any]:
        """Test HubSpot connection"""
        if not self.config:
            return {"status": "not_configured", "error": "HubSpot adapter not initialized"}
        
        try:
            async with HubSpotClient(self.config) as client:
                # Test with a simple API call
                await client.search_contacts(limit=1)
                
                return {
                    "status": "connected",
                    "platform": "hubspot",
                    "organization_id": organization_id
                }
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "platform": "hubspot"
            }

# Global instance
hubspot_adapter = HubSpotAdapter()

