"""
Metabase Business Intelligence Service
Enterprise-grade BI with embedded dashboards and FACE module integration
"""

import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import jwt
import json

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    CUSTOM = "custom"

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    TABLE = "table"
    METRIC = "metric"
    FUNNEL = "funnel"

class Dashboard(BaseModel):
    """Dashboard definition"""
    id: int
    name: str
    description: str
    dashboard_type: DashboardType
    organization_id: str
    charts: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

class Chart(BaseModel):
    """Chart definition"""
    id: int
    name: str
    chart_type: ChartType
    query: str
    visualization_settings: Dict[str, Any]
    dashboard_id: int
    position_x: int
    position_y: int
    width: int
    height: int

class MetabaseService:
    """
    Metabase Business Intelligence Service
    Manages dashboards, charts, and embedded analytics
    """

    def __init__(self):
        self.enable_metabase = os.getenv("ENABLE_METABASE", "false").lower() == "true"
        self.metabase_url = os.getenv("METABASE_URL", "http://metabase:3000")
        self.embedding_secret = os.getenv("METABASE_EMBEDDING_SECRET", "your-metabase-embedding-secret")
        self.site_url = os.getenv("METABASE_SITE_URL", "http://metabase.omnify.local")
        self.admin_email = os.getenv("METABASE_ADMIN_EMAIL", "admin@omnify.local")
        self.admin_password = os.getenv("METABASE_ADMIN_PASSWORD", "admin123")
        self.timeout = int(os.getenv("METABASE_TIMEOUT", "30"))
        
        # HTTP client for Metabase API
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.metabase_url
        )

        # Authentication
        self.session_token: Optional[str] = None
        self.api_key: Optional[str] = None

        # Dashboard templates
        self.dashboard_templates = self._create_dashboard_templates()

        logger.info(f"Metabase Service initialized", extra={
            "enabled": self.enable_metabase,
            "metabase_url": self.metabase_url,
            "site_url": self.site_url
        })

    def _create_dashboard_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create dashboard templates for FACE module"""
        return {
            "executive_dashboard": {
                "name": "Executive Dashboard",
                "description": "High-level KPIs and business metrics",
                "dashboard_type": DashboardType.EXECUTIVE,
                "charts": [
                    {
                        "name": "Revenue Overview",
                        "chart_type": ChartType.METRIC,
                        "query": "SELECT SUM(revenue) FROM campaigns WHERE created_at >= NOW() - INTERVAL '30 days'",
                        "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "Campaign Performance",
                        "chart_type": ChartType.BAR,
                        "query": "SELECT platform, SUM(clicks) as clicks FROM campaigns GROUP BY platform",
                        "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "name": "Customer Acquisition",
                        "chart_type": ChartType.LINE,
                        "query": "SELECT DATE(created_at) as date, COUNT(*) as customers FROM customers GROUP BY DATE(created_at)",
                        "position": {"x": 0, "y": 4, "width": 12, "height": 4}
                    }
                ]
            },
            "operational_dashboard": {
                "name": "Operational Dashboard",
                "description": "Day-to-day operational metrics",
                "dashboard_type": DashboardType.OPERATIONAL,
                "charts": [
                    {
                        "name": "Active Campaigns",
                        "chart_type": ChartType.TABLE,
                        "query": "SELECT name, status, budget, spent FROM campaigns WHERE status = 'active'",
                        "position": {"x": 0, "y": 0, "width": 12, "height": 6}
                    },
                    {
                        "name": "Platform Performance",
                        "chart_type": ChartType.PIE,
                        "query": "SELECT platform, SUM(spent) as spent FROM campaigns GROUP BY platform",
                        "position": {"x": 0, "y": 6, "width": 6, "height": 4}
                    },
                    {
                        "name": "Conversion Funnel",
                        "chart_type": ChartType.FUNNEL,
                        "query": "SELECT stage, COUNT(*) as count FROM conversions GROUP BY stage",
                        "position": {"x": 6, "y": 6, "width": 6, "height": 4}
                    }
                ]
            },
            "analytical_dashboard": {
                "name": "Analytical Dashboard",
                "description": "Deep dive analytics and insights",
                "dashboard_type": DashboardType.ANALYTICAL,
                "charts": [
                    {
                        "name": "Cohort Analysis",
                        "chart_type": ChartType.TABLE,
                        "query": "SELECT cohort_month, COUNT(*) as customers FROM customer_cohorts GROUP BY cohort_month",
                        "position": {"x": 0, "y": 0, "width": 12, "height": 6}
                    },
                    {
                        "name": "Customer Segmentation",
                        "chart_type": ChartType.SCATTER,
                        "query": "SELECT ltv, frequency FROM customers WHERE ltv > 0",
                        "position": {"x": 0, "y": 6, "width": 6, "height": 4}
                    },
                    {
                        "name": "Churn Prediction",
                        "chart_type": ChartType.BAR,
                        "query": "SELECT churn_risk, COUNT(*) as customers FROM customer_segments GROUP BY churn_risk",
                        "position": {"x": 6, "y": 6, "width": 6, "height": 4}
                    }
                ]
            }
        }

    async def authenticate(self) -> bool:
        """Authenticate with Metabase"""
        try:
            if not self.enable_metabase:
                return False

            # Try to get session token
            login_data = {
                "username": self.admin_email,
                "password": self.admin_password
            }

            response = await self.http_client.post("/api/session", json=login_data)
            
            if response.status_code == 200:
                session_data = response.json()
                self.session_token = session_data.get("id")
                
                # Set session token in headers
                self.http_client.headers.update({"X-Metabase-Session": self.session_token})
                
                logger.info("Metabase authentication successful")
                return True
            else:
                logger.error(f"Metabase authentication failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Metabase authentication error: {str(e)}")
            return False

    async def create_database_connection(self, organization_id: str) -> Dict[str, Any]:
        """Create database connection for organization"""
        try:
            if not self.session_token:
                await self.authenticate()

            # Create database connection
            db_config = {
                "engine": "mongodb",
                "name": f"omnify-{organization_id}",
                "details": {
                    "host": os.getenv("MONGO_HOST", "mongodb"),
                    "port": int(os.getenv("MONGO_PORT", "27017")),
                    "dbname": f"omnify_{organization_id}",
                    "user": os.getenv("MONGO_USER", ""),
                    "password": os.getenv("MONGO_PASSWORD", ""),
                    "ssl": False
                }
            }

            response = await self.http_client.post("/api/database", json=db_config)
            
            if response.status_code == 200:
                db_data = response.json()
                logger.info(f"Database connection created for organization {organization_id}")
                return db_data
            else:
                logger.error(f"Failed to create database connection: {response.status_code}")
                return {"error": "Failed to create database connection"}

        except Exception as e:
            logger.error(f"Database connection creation failed: {str(e)}")
            return {"error": str(e)}

    async def create_dashboard(self, template_name: str, organization_id: str) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            if not self.session_token:
                await self.authenticate()

            if template_name not in self.dashboard_templates:
                raise ValueError(f"Template {template_name} not found")

            template = self.dashboard_templates[template_name]
            
            # Create dashboard
            dashboard_data = {
                "name": f"{template['name']} - {organization_id}",
                "description": template["description"],
                "parameters": [],
                "public_uuid": None
            }

            response = await self.http_client.post("/api/dashboard", json=dashboard_data)
            
            if response.status_code == 200:
                dashboard = response.json()
                dashboard_id = dashboard["id"]
                
                # Create charts for dashboard
                charts = []
                for chart_template in template["charts"]:
                    chart_data = {
                        "name": chart_template["name"],
                        "description": f"Chart for {chart_template['name']}",
                        "display": chart_template["chart_type"].value,
                        "dataset_query": {
                            "database": 1,  # Would be dynamic in production
                            "type": "native",
                            "native": {
                                "query": chart_template["query"]
                            }
                        },
                        "visualization_settings": {},
                        "dashboard_id": dashboard_id,
                        "row": chart_template["position"]["y"],
                        "col": chart_template["position"]["x"],
                        "size_x": chart_template["position"]["width"],
                        "size_y": chart_template["position"]["height"]
                    }
                    
                    chart_response = await self.http_client.post("/api/card", json=chart_data)
                    if chart_response.status_code == 200:
                        charts.append(chart_response.json())
                
                logger.info(f"Dashboard created: {template_name}", extra={
                    "dashboard_id": dashboard_id,
                    "organization_id": organization_id,
                    "charts_created": len(charts)
                })

                return {
                    "dashboard_id": dashboard_id,
                    "name": template["name"],
                    "charts": charts,
                    "organization_id": organization_id
                }
            else:
                logger.error(f"Failed to create dashboard: {response.status_code}")
                return {"error": "Failed to create dashboard"}

        except Exception as e:
            logger.error(f"Dashboard creation failed: {str(e)}")
            return {"error": str(e)}

    async def generate_embedding_token(
        self,
        dashboard_id: int,
        organization_id: str,
        user_id: str,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Generate embedding token for dashboard"""
        try:
            if not expires_at:
                expires_at = datetime.utcnow() + timedelta(hours=24)

            # Create JWT payload
            payload = {
                "resource": {"dashboard": dashboard_id},
                "params": {
                    "organization_id": organization_id,
                    "user_id": user_id
                },
                "exp": int(expires_at.timestamp())
            }

            # Generate JWT token
            token = jwt.encode(payload, self.embedding_secret, algorithm="HS256")
            
            logger.info(f"Embedding token generated", extra={
                "dashboard_id": dashboard_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "expires_at": expires_at.isoformat()
            })

            return token

        except Exception as e:
            logger.error(f"Failed to generate embedding token: {str(e)}")
            raise

    async def get_dashboard_embed_url(
        self,
        dashboard_id: int,
        organization_id: str,
        user_id: str
    ) -> str:
        """Get embedded dashboard URL"""
        try:
            token = await self.generate_embedding_token(dashboard_id, organization_id, user_id)
            
            embed_url = f"{self.site_url}/embed/dashboard/{token}#bordered=true&titled=true"
            
            return embed_url

        except Exception as e:
            logger.error(f"Failed to get embed URL: {str(e)}")
            raise

    async def get_dashboard_data(self, dashboard_id: int) -> Dict[str, Any]:
        """Get dashboard data and metadata"""
        try:
            if not self.session_token:
                await self.authenticate()

            response = await self.http_client.get(f"/api/dashboard/{dashboard_id}")
            
            if response.status_code == 200:
                dashboard = response.json()
                
                # Get dashboard cards (charts)
                cards_response = await self.http_client.get(f"/api/dashboard/{dashboard_id}/cards")
                cards = cards_response.json() if cards_response.status_code == 200 else []
                
                return {
                    "dashboard": dashboard,
                    "cards": cards,
                    "total_cards": len(cards)
                }
            else:
                logger.error(f"Failed to get dashboard data: {response.status_code}")
                return {"error": "Failed to get dashboard data"}

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {str(e)}")
            return {"error": str(e)}

    async def create_face_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Create FACE module dashboard"""
        try:
            # Create executive dashboard
            executive_result = await self.create_dashboard("executive_dashboard", organization_id)
            
            # Create operational dashboard
            operational_result = await self.create_dashboard("operational_dashboard", organization_id)
            
            # Create analytical dashboard
            analytical_result = await self.create_dashboard("analytical_dashboard", organization_id)
            
            # Generate embedding URLs
            dashboards = []
            
            if "dashboard_id" in executive_result:
                embed_url = await self.get_dashboard_embed_url(
                    executive_result["dashboard_id"], organization_id, "system"
                )
                dashboards.append({
                    "type": "executive",
                    "dashboard_id": executive_result["dashboard_id"],
                    "embed_url": embed_url,
                    "name": executive_result["name"]
                })
            
            if "dashboard_id" in operational_result:
                embed_url = await self.get_dashboard_embed_url(
                    operational_result["dashboard_id"], organization_id, "system"
                )
                dashboards.append({
                    "type": "operational",
                    "dashboard_id": operational_result["dashboard_id"],
                    "embed_url": embed_url,
                    "name": operational_result["name"]
                })
            
            if "dashboard_id" in analytical_result:
                embed_url = await self.get_dashboard_embed_url(
                    analytical_result["dashboard_id"], organization_id, "system"
                )
                dashboards.append({
                    "type": "analytical",
                    "dashboard_id": analytical_result["dashboard_id"],
                    "embed_url": embed_url,
                    "name": analytical_result["name"]
                })

            logger.info(f"FACE dashboard created for organization {organization_id}", extra={
                "dashboards_created": len(dashboards),
                "organization_id": organization_id
            })

            return {
                "status": "success",
                "organization_id": organization_id,
                "dashboards": dashboards,
                "total_dashboards": len(dashboards)
            }

        except Exception as e:
            logger.error(f"FACE dashboard creation failed: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for Metabase service"""
        try:
            if not self.enable_metabase:
                return {
                    "status": "disabled",
                    "metabase_enabled": False,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Test Metabase connectivity
            response = await self.http_client.get("/api/health")
            metabase_status = "healthy" if response.status_code == 200 else "unhealthy"

            # Check authentication
            authenticated = self.session_token is not None

            return {
                "status": "healthy" if metabase_status == "healthy" and authenticated else "degraded",
                "metabase_enabled": self.enable_metabase,
                "metabase_status": metabase_status,
                "authenticated": authenticated,
                "site_url": self.site_url,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Metabase health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

# Global instance
metabase_service = MetabaseService()
