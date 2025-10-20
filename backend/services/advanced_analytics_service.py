"""
Advanced Analytics & Reporting System
Production-grade analytics with real-time dashboards, custom report builder, and scheduled reports
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import base64
import io
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class ReportFormat(str, Enum):
    """Supported report formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    POWERPOINT = "powerpoint"
    HTML = "html"

class ReportType(str, Enum):
    """Report types"""
    PERFORMANCE = "performance"
    FINANCIAL = "financial"
    AUDIENCE = "audience"
    CREATIVE = "creative"
    COMPETITIVE = "competitive"
    CUSTOM = "custom"

class DashboardType(str, Enum):
    """Dashboard types"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    CUSTOM = "custom"

@dataclass
class ChartConfig:
    """Chart configuration"""
    chart_type: str
    title: str
    x_axis: str
    y_axis: str
    color_by: Optional[str] = None
    filters: Dict[str, Any] = None
    time_range: str = "30d"
    aggregation: str = "sum"

@dataclass
class ReportConfig:
    """Report configuration"""
    name: str
    description: str
    report_type: ReportType
    format: ReportFormat
    schedule: Optional[str] = None
    recipients: List[str] = None
    charts: List[ChartConfig] = None
    filters: Dict[str, Any] = None
    time_range: str = "30d"

class AnalyticsDataProcessor:
    """Processes analytics data for reports and dashboards"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def get_campaign_metrics(self, client_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive campaign metrics"""
        try:
            # Aggregate campaign performance data
            pipeline = [
                {
                    "$match": {
                        "client_id": client_id,
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$platform",
                        "total_impressions": {"$sum": "$impressions"},
                        "total_clicks": {"$sum": "$clicks"},
                        "total_conversions": {"$sum": "$conversions"},
                        "total_cost": {"$sum": "$cost"},
                        "total_revenue": {"$sum": "$revenue"},
                        "avg_cpa": {"$avg": "$cpa"},
                        "avg_roas": {"$avg": "$roas"},
                        "avg_ctr": {"$avg": "$ctr"},
                        "avg_conversion_rate": {"$avg": "$conversion_rate"},
                        "campaign_count": {"$sum": 1}
                    }
                }
            ]
            
            results = await self.db.performance_metrics.aggregate(pipeline).to_list(length=None)
            
            # Calculate additional metrics
            total_impressions = sum(r["total_impressions"] for r in results)
            total_clicks = sum(r["total_clicks"] for r in results)
            total_conversions = sum(r["total_conversions"] for r in results)
            total_cost = sum(r["total_cost"] for r in results)
            total_revenue = sum(r["total_revenue"] for r in results)
            
            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            overall_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0
            overall_roas = (total_revenue / total_cost) if total_cost > 0 else 0
            
            return {
                "platforms": results,
                "overall": {
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "total_cost": total_cost,
                    "total_revenue": total_revenue,
                    "overall_ctr": overall_ctr,
                    "overall_conversion_rate": overall_conversion_rate,
                    "overall_cpa": overall_cpa,
                    "overall_roas": overall_roas
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign metrics: {e}")
            raise
    
    async def get_audience_insights(self, client_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audience insights and demographics"""
        try:
            # Get audience data
            pipeline = [
                {
                    "$match": {
                        "client_id": client_id,
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "age_group": "$audience.age_group",
                            "gender": "$audience.gender",
                            "location": "$audience.location"
                        },
                        "impressions": {"$sum": "$impressions"},
                        "clicks": {"$sum": "$clicks"},
                        "conversions": {"$sum": "$conversions"},
                        "cost": {"$sum": "$cost"},
                        "revenue": {"$sum": "$revenue"}
                    }
                }
            ]
            
            results = await self.db.performance_metrics.aggregate(pipeline).to_list(length=None)
            
            # Process audience insights
            age_groups = {}
            genders = {}
            locations = {}
            
            for result in results:
                audience = result["_id"]
                
                # Age group analysis
                age_group = audience.get("age_group", "unknown")
                if age_group not in age_groups:
                    age_groups[age_group] = {"impressions": 0, "clicks": 0, "conversions": 0, "cost": 0, "revenue": 0}
                for key in ["impressions", "clicks", "conversions", "cost", "revenue"]:
                    age_groups[age_group][key] += result[key]
                
                # Gender analysis
                gender = audience.get("gender", "unknown")
                if gender not in genders:
                    genders[gender] = {"impressions": 0, "clicks": 0, "conversions": 0, "cost": 0, "revenue": 0}
                for key in ["impressions", "clicks", "conversions", "cost", "revenue"]:
                    genders[gender][key] += result[key]
                
                # Location analysis
                location = audience.get("location", "unknown")
                if location not in locations:
                    locations[location] = {"impressions": 0, "clicks": 0, "conversions": 0, "cost": 0, "revenue": 0}
                for key in ["impressions", "clicks", "conversions", "cost", "revenue"]:
                    locations[location][key] += result[key]
            
            return {
                "age_groups": age_groups,
                "genders": genders,
                "locations": locations,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting audience insights: {e}")
            raise
    
    async def get_creative_performance(self, client_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get creative performance analysis"""
        try:
            # Get creative performance data
            pipeline = [
                {
                    "$match": {
                        "client_id": client_id,
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "creative_id": "$creative.id",
                            "creative_type": "$creative.type",
                            "platform": "$platform"
                        },
                        "impressions": {"$sum": "$impressions"},
                        "clicks": {"$sum": "$clicks"},
                        "conversions": {"$sum": "$conversions"},
                        "cost": {"$sum": "$cost"},
                        "revenue": {"$sum": "$revenue"},
                        "ctr": {"$avg": "$ctr"},
                        "conversion_rate": {"$avg": "$conversion_rate"},
                        "cpa": {"$avg": "$cpa"},
                        "roas": {"$avg": "$roas"}
                    }
                },
                {
                    "$sort": {"revenue": -1}
                }
            ]
            
            results = await self.db.performance_metrics.aggregate(pipeline).to_list(length=None)
            
            # Analyze creative performance
            top_performers = results[:10]
            creative_types = {}
            platform_performance = {}
            
            for result in results:
                creative_type = result["_id"]["creative_type"]
                platform = result["_id"]["platform"]
                
                if creative_type not in creative_types:
                    creative_types[creative_type] = {"count": 0, "total_revenue": 0, "avg_roas": 0}
                creative_types[creative_type]["count"] += 1
                creative_types[creative_type]["total_revenue"] += result["revenue"]
                
                if platform not in platform_performance:
                    platform_performance[platform] = {"count": 0, "total_revenue": 0, "avg_roas": 0}
                platform_performance[platform]["count"] += 1
                platform_performance[platform]["total_revenue"] += result["revenue"]
            
            # Calculate averages
            for creative_type in creative_types:
                if creative_types[creative_type]["count"] > 0:
                    creative_types[creative_type]["avg_roas"] = creative_types[creative_type]["total_revenue"] / creative_types[creative_type]["count"]
            
            for platform in platform_performance:
                if platform_performance[platform]["count"] > 0:
                    platform_performance[platform]["avg_roas"] = platform_performance[platform]["total_revenue"] / platform_performance[platform]["count"]
            
            return {
                "top_performers": top_performers,
                "creative_types": creative_types,
                "platform_performance": platform_performance,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting creative performance: {e}")
            raise

class ChartGenerator:
    """Generates interactive charts for dashboards and reports"""
    
    def __init__(self):
        self.chart_templates = {
            "line": self._create_line_chart,
            "bar": self._create_bar_chart,
            "pie": self._create_pie_chart,
            "scatter": self._create_scatter_chart,
            "area": self._create_area_chart,
            "heatmap": self._create_heatmap,
            "funnel": self._create_funnel_chart
        }
    
    def generate_chart(self, chart_config: ChartConfig, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate chart based on configuration and data"""
        try:
            if chart_config.chart_type not in self.chart_templates:
                raise ValueError(f"Unsupported chart type: {chart_config.chart_type}")
            
            chart_func = self.chart_templates[chart_config.chart_type]
            fig = chart_func(chart_config, data)
            
            # Convert to JSON
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
            
            return {
                "chart_id": str(uuid.uuid4()),
                "chart_type": chart_config.chart_type,
                "title": chart_config.title,
                "data": chart_json,
                "config": asdict(chart_config),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            raise
    
    def _create_line_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create line chart"""
        df = pd.DataFrame(data)
        
        fig = px.line(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=config.title
        )
        
        fig.update_layout(
            xaxis_title=config.x_axis.replace("_", " ").title(),
            yaxis_title=config.y_axis.replace("_", " ").title(),
            hovermode='x unified'
        )
        
        return fig
    
    def _create_bar_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create bar chart"""
        df = pd.DataFrame(data)
        
        fig = px.bar(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=config.title
        )
        
        fig.update_layout(
            xaxis_title=config.x_axis.replace("_", " ").title(),
            yaxis_title=config.y_axis.replace("_", " ").title()
        )
        
        return fig
    
    def _create_pie_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create pie chart"""
        df = pd.DataFrame(data)
        
        fig = px.pie(
            df,
            names=config.x_axis,
            values=config.y_axis,
            title=config.title
        )
        
        return fig
    
    def _create_scatter_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create scatter chart"""
        df = pd.DataFrame(data)
        
        fig = px.scatter(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=config.title
        )
        
        fig.update_layout(
            xaxis_title=config.x_axis.replace("_", " ").title(),
            yaxis_title=config.y_axis.replace("_", " ").title()
        )
        
        return fig
    
    def _create_area_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create area chart"""
        df = pd.DataFrame(data)
        
        fig = px.area(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=config.title
        )
        
        fig.update_layout(
            xaxis_title=config.x_axis.replace("_", " ").title(),
            yaxis_title=config.y_axis.replace("_", " ").title()
        )
        
        return fig
    
    def _create_heatmap(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create heatmap"""
        df = pd.DataFrame(data)
        
        # Pivot data for heatmap
        pivot_df = df.pivot_table(
            index=config.x_axis,
            columns=config.color_by,
            values=config.y_axis,
            aggfunc='sum',
            fill_value=0
        )
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            title=config.title,
            color_continuous_scale='Viridis'
        )
        
        return fig
    
    def _create_funnel_chart(self, config: ChartConfig, data: List[Dict[str, Any]]) -> go.Figure:
        """Create funnel chart"""
        df = pd.DataFrame(data)
        
        fig = go.Figure(go.Funnel(
            y=df[config.x_axis].tolist(),
            x=df[config.y_axis].tolist(),
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(title=config.title)
        
        return fig

class ReportGenerator:
    """Generates reports in various formats"""
    
    def __init__(self, chart_generator: ChartGenerator):
        self.chart_generator = chart_generator
    
    async def generate_report(self, report_config: ReportConfig, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report based on configuration and data"""
        try:
            report_id = str(uuid.uuid4())
            
            # Generate charts
            charts = []
            if report_config.charts:
                for chart_config in report_config.charts:
                    chart_data = self._extract_chart_data(chart_config, data)
                    chart = self.chart_generator.generate_chart(chart_config, chart_data)
                    charts.append(chart)
            
            # Generate report content
            report_content = {
                "report_id": report_id,
                "name": report_config.name,
                "description": report_config.description,
                "report_type": report_config.report_type,
                "format": report_config.format,
                "generated_at": datetime.utcnow().isoformat(),
                "period": data.get("period", {}),
                "summary": self._generate_summary(data),
                "charts": charts,
                "data": data
            }
            
            # Generate file based on format
            if report_config.format == ReportFormat.PDF:
                file_content = await self._generate_pdf_report(report_content)
            elif report_config.format == ReportFormat.EXCEL:
                file_content = await self._generate_excel_report(report_content)
            elif report_config.format == ReportFormat.CSV:
                file_content = await self._generate_csv_report(report_content)
            elif report_config.format == ReportFormat.POWERPOINT:
                file_content = await self._generate_powerpoint_report(report_content)
            elif report_config.format == ReportFormat.HTML:
                file_content = await self._generate_html_report(report_content)
            else:
                raise ValueError(f"Unsupported report format: {report_config.format}")
            
            return {
                "report_id": report_id,
                "report_content": report_content,
                "file_content": file_content,
                "file_size": len(file_content),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _extract_chart_data(self, chart_config: ChartConfig, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data for specific chart"""
        # This would extract relevant data based on chart configuration
        # For now, return sample data
        return [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150},
            {"date": "2024-01-03", "value": 200}
        ]
    
    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report summary"""
        return {
            "total_campaigns": data.get("overall", {}).get("total_campaigns", 0),
            "total_spend": data.get("overall", {}).get("total_cost", 0),
            "total_revenue": data.get("overall", {}).get("total_revenue", 0),
            "roas": data.get("overall", {}).get("overall_roas", 0),
            "cpa": data.get("overall", {}).get("overall_cpa", 0)
        }
    
    async def _generate_pdf_report(self, report_content: Dict[str, Any]) -> bytes:
        """Generate PDF report"""
        # This would use a PDF generation library like reportlab
        # For now, return sample PDF content
        return b"PDF report content"
    
    async def _generate_excel_report(self, report_content: Dict[str, Any]) -> bytes:
        """Generate Excel report"""
        # This would use openpyxl or xlsxwriter
        # For now, return sample Excel content
        return b"Excel report content"
    
    async def _generate_csv_report(self, report_content: Dict[str, Any]) -> bytes:
        """Generate CSV report"""
        # Convert data to CSV
        csv_content = "metric,value\n"
        csv_content += f"total_campaigns,{report_content['summary']['total_campaigns']}\n"
        csv_content += f"total_spend,{report_content['summary']['total_spend']}\n"
        csv_content += f"total_revenue,{report_content['summary']['total_revenue']}\n"
        csv_content += f"roas,{report_content['summary']['roas']}\n"
        csv_content += f"cpa,{report_content['summary']['cpa']}\n"
        
        return csv_content.encode('utf-8')
    
    async def _generate_powerpoint_report(self, report_content: Dict[str, Any]) -> bytes:
        """Generate PowerPoint report"""
        # This would use python-pptx
        # For now, return sample PowerPoint content
        return b"PowerPoint report content"
    
    async def _generate_html_report(self, report_content: Dict[str, Any]) -> bytes:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_content['name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_content['name']}</h1>
                <p>{report_content['description']}</p>
                <p>Generated: {report_content['generated_at']}</p>
            </div>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Campaigns: {report_content['summary']['total_campaigns']}</p>
                <p>Total Spend: ${report_content['summary']['total_spend']:,.2f}</p>
                <p>Total Revenue: ${report_content['summary']['total_revenue']:,.2f}</p>
                <p>ROAS: {report_content['summary']['roas']:.2f}</p>
                <p>CPA: ${report_content['summary']['cpa']:.2f}</p>
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')

class DashboardManager:
    """Manages real-time dashboards"""
    
    def __init__(self, db: AsyncIOMotorClient, chart_generator: ChartGenerator):
        self.db = db
        self.chart_generator = chart_generator
        self.active_dashboards = {}
    
    async def create_dashboard(self, client_id: str, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        try:
            dashboard_id = str(uuid.uuid4())
            
            dashboard = {
                "dashboard_id": dashboard_id,
                "client_id": client_id,
                "name": dashboard_config["name"],
                "description": dashboard_config.get("description", ""),
                "dashboard_type": dashboard_config.get("dashboard_type", DashboardType.CUSTOM),
                "charts": dashboard_config.get("charts", []),
                "layout": dashboard_config.get("layout", {}),
                "filters": dashboard_config.get("filters", {}),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Save to database
            await self.db.dashboards.insert_one(dashboard)
            
            # Add to active dashboards
            self.active_dashboards[dashboard_id] = dashboard
            
            logger.info(f"Created dashboard {dashboard_id} for client {client_id}")
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        try:
            dashboard = await self.db.dashboards.find_one({"dashboard_id": dashboard_id})
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            # Get data processor
            data_processor = AnalyticsDataProcessor(self.db)
            
            # Calculate time range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)  # Default 30 days
            
            # Get metrics data
            metrics_data = await data_processor.get_campaign_metrics(
                dashboard["client_id"], start_date, end_date
            )
            
            # Generate charts
            charts = []
            for chart_config in dashboard.get("charts", []):
                chart_data = self._extract_chart_data(chart_config, metrics_data)
                chart = self.chart_generator.generate_chart(chart_config, chart_data)
                charts.append(chart)
            
            return {
                "dashboard_id": dashboard_id,
                "name": dashboard["name"],
                "description": dashboard["description"],
                "dashboard_type": dashboard["dashboard_type"],
                "charts": charts,
                "metrics": metrics_data,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise
    
    def _extract_chart_data(self, chart_config: Dict[str, Any], metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data for chart from metrics"""
        # This would extract relevant data based on chart configuration
        # For now, return sample data
        return [
            {"platform": "Google Ads", "revenue": 10000, "cost": 5000},
            {"platform": "Meta Ads", "revenue": 8000, "cost": 4000},
            {"platform": "LinkedIn", "revenue": 5000, "cost": 2500}
        ]

class ScheduledReportManager:
    """Manages scheduled reports"""
    
    def __init__(self, db: AsyncIOMotorClient, report_generator: ReportGenerator):
        self.db = db
        self.report_generator = report_generator
        self.scheduled_reports = {}
    
    async def create_scheduled_report(self, client_id: str, report_config: ReportConfig) -> Dict[str, Any]:
        """Create a scheduled report"""
        try:
            report_id = str(uuid.uuid4())
            
            scheduled_report = {
                "report_id": report_id,
                "client_id": client_id,
                "name": report_config.name,
                "description": report_config.description,
                "report_type": report_config.report_type,
                "format": report_config.format,
                "schedule": report_config.schedule,
                "recipients": report_config.recipients or [],
                "charts": [asdict(chart) for chart in report_config.charts] if report_config.charts else [],
                "filters": report_config.filters or {},
                "time_range": report_config.time_range,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "last_run": None,
                "next_run": self._calculate_next_run(report_config.schedule)
            }
            
            # Save to database
            await self.db.scheduled_reports.insert_one(scheduled_report)
            
            # Add to active scheduled reports
            self.scheduled_reports[report_id] = scheduled_report
            
            logger.info(f"Created scheduled report {report_id} for client {client_id}")
            
            return scheduled_report
            
        except Exception as e:
            logger.error(f"Error creating scheduled report: {e}")
            raise
    
    async def execute_scheduled_report(self, report_id: str) -> Dict[str, Any]:
        """Execute a scheduled report"""
        try:
            scheduled_report = await self.db.scheduled_reports.find_one({"report_id": report_id})
            if not scheduled_report:
                raise ValueError(f"Scheduled report {report_id} not found")
            
            # Get data processor
            data_processor = AnalyticsDataProcessor(self.db)
            
            # Calculate time range
            end_date = datetime.utcnow()
            if scheduled_report["time_range"] == "7d":
                start_date = end_date - timedelta(days=7)
            elif scheduled_report["time_range"] == "30d":
                start_date = end_date - timedelta(days=30)
            elif scheduled_report["time_range"] == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get metrics data
            metrics_data = await data_processor.get_campaign_metrics(
                scheduled_report["client_id"], start_date, end_date
            )
            
            # Generate report
            report_config = ReportConfig(
                name=scheduled_report["name"],
                description=scheduled_report["description"],
                report_type=scheduled_report["report_type"],
                format=scheduled_report["format"],
                charts=[ChartConfig(**chart) for chart in scheduled_report["charts"]],
                filters=scheduled_report["filters"],
                time_range=scheduled_report["time_range"]
            )
            
            report_result = await self.report_generator.generate_report(report_config, metrics_data)
            
            # Send report to recipients
            if scheduled_report["recipients"]:
                await self._send_report_email(report_result, scheduled_report["recipients"])
            
            # Update last run time
            await self.db.scheduled_reports.update_one(
                {"report_id": report_id},
                {
                    "$set": {
                        "last_run": datetime.utcnow().isoformat(),
                        "next_run": self._calculate_next_run(scheduled_report["schedule"])
                    }
                }
            )
            
            logger.info(f"Executed scheduled report {report_id}")
            
            return report_result
            
        except Exception as e:
            logger.error(f"Error executing scheduled report: {e}")
            raise
    
    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time based on schedule"""
        now = datetime.utcnow()
        
        if schedule == "daily":
            next_run = now + timedelta(days=1)
        elif schedule == "weekly":
            next_run = now + timedelta(weeks=1)
        elif schedule == "monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.isoformat()
    
    async def _send_report_email(self, report_result: Dict[str, Any], recipients: List[str]):
        """Send report via email"""
        try:
            # This would implement actual email sending
            # For now, just log the action
            logger.info(f"Sending report {report_result['report_id']} to {recipients}")
            
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
            raise

class AdvancedAnalyticsService:
    """Main service for advanced analytics and reporting"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.chart_generator = ChartGenerator()
        self.report_generator = ReportGenerator(self.chart_generator)
        self.dashboard_manager = DashboardManager(db, self.chart_generator)
        self.scheduled_report_manager = ScheduledReportManager(db, self.report_generator)
        self.data_processor = AnalyticsDataProcessor(db)
    
    async def get_real_time_metrics(self, client_id: str) -> Dict[str, Any]:
        """Get real-time metrics for dashboard"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)  # Last 7 days
            
            metrics = await self.data_processor.get_campaign_metrics(client_id, start_date, end_date)
            
            return {
                "client_id": client_id,
                "metrics": metrics,
                "last_updated": datetime.utcnow().isoformat(),
                "time_range": "7d"
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            raise
    
    async def create_custom_dashboard(self, client_id: str, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom dashboard"""
        return await self.dashboard_manager.create_dashboard(client_id, dashboard_config)
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data"""
        return await self.dashboard_manager.get_dashboard_data(dashboard_id)
    
    async def generate_custom_report(self, client_id: str, report_config: ReportConfig) -> Dict[str, Any]:
        """Generate custom report"""
        try:
            # Calculate time range
            end_date = datetime.utcnow()
            if report_config.time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif report_config.time_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif report_config.time_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get data
            metrics_data = await self.data_processor.get_campaign_metrics(client_id, start_date, end_date)
            
            # Generate report
            return await self.report_generator.generate_report(report_config, metrics_data)
            
        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            raise
    
    async def create_scheduled_report(self, client_id: str, report_config: ReportConfig) -> Dict[str, Any]:
        """Create scheduled report"""
        return await self.scheduled_report_manager.create_scheduled_report(client_id, report_config)
    
    async def get_audience_insights(self, client_id: str, time_range: str = "30d") -> Dict[str, Any]:
        """Get audience insights"""
        try:
            end_date = datetime.utcnow()
            if time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            return await self.data_processor.get_audience_insights(client_id, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error getting audience insights: {e}")
            raise
    
    async def get_creative_performance(self, client_id: str, time_range: str = "30d") -> Dict[str, Any]:
        """Get creative performance analysis"""
        try:
            end_date = datetime.utcnow()
            if time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            return await self.data_processor.get_creative_performance(client_id, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error getting creative performance: {e}")
            raise

# Global instance
advanced_analytics_service = None

def get_advanced_analytics_service(db: AsyncIOMotorClient) -> AdvancedAnalyticsService:
    """Get advanced analytics service instance"""
    global advanced_analytics_service
    if advanced_analytics_service is None:
        advanced_analytics_service = AdvancedAnalyticsService(db)
    return advanced_analytics_service
