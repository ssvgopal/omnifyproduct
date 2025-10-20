"""
Advanced Reporting & BI System
Production-grade reporting with custom dashboards, data visualization, and executive reports
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import pandas as pd
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import aiohttp
import jinja2
from weasyprint import HTML, CSS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class ReportType(str, Enum):
    """Report types"""
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    FINANCIAL_SUMMARY = "financial_summary"
    AUDIENCE_ANALYTICS = "audience_analytics"
    CONVERSION_FUNNEL = "conversion_funnel"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    CUSTOM_DASHBOARD = "custom_dashboard"

class ChartType(str, Enum):
    """Chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    TREEMAP = "treemap"
    SANKEY = "sankey"

class ReportFormat(str, Enum):
    """Report formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    PNG = "png"
    SVG = "svg"

class ReportStatus(str, Enum):
    """Report status"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"

@dataclass
class ReportTemplate:
    """Report template definition"""
    template_id: str
    name: str
    description: str
    report_type: ReportType
    chart_configs: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    layout: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ReportInstance:
    """Report instance"""
    report_id: str
    template_id: str
    name: str
    status: ReportStatus
    parameters: Dict[str, Any]
    generated_at: Optional[datetime]
    file_path: Optional[str]
    file_size: Optional[int]
    created_by: str
    created_at: datetime

@dataclass
class DashboardWidget:
    """Dashboard widget definition"""
    widget_id: str
    name: str
    chart_type: ChartType
    data_source: str
    config: Dict[str, Any]
    position: Dict[str, int]
    size: Dict[str, int]
    refresh_interval: int

class DataAggregator:
    """Aggregates data from multiple sources for reporting"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def aggregate_campaign_data(self, date_range: Tuple[datetime, datetime], filters: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate campaign data for reporting"""
        try:
            start_date, end_date = date_range
            
            # Build query
            query = {
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
            
            # Add filters
            if filters.get("platform"):
                query["platform"] = filters["platform"]
            if filters.get("status"):
                query["status"] = filters["status"]
            if filters.get("campaign_type"):
                query["campaign_type"] = filters["campaign_type"]
            
            # Get campaign data
            campaigns = await self.db.campaigns.find(query).to_list(length=None)
            
            if not campaigns:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(campaigns)
            
            # Get metrics for each campaign
            campaign_ids = [c["campaign_id"] for c in campaigns]
            metrics = await self.db.campaign_metrics.find({
                "campaign_id": {"$in": campaign_ids}
            }).to_list(length=None)
            
            # Merge metrics with campaigns
            metrics_df = pd.DataFrame(metrics)
            if not metrics_df.empty:
                df = df.merge(metrics_df, on="campaign_id", how="left")
            
            # Calculate derived metrics
            df["roas"] = df["revenue"] / df["spend"]
            df["cpa"] = df["spend"] / df["conversions"]
            df["ctr"] = df["clicks"] / df["impressions"]
            df["conversion_rate"] = df["conversions"] / df["clicks"]
            
            return df
            
        except Exception as e:
            logger.error(f"Error aggregating campaign data: {e}")
            return pd.DataFrame()
    
    async def aggregate_financial_data(self, date_range: Tuple[datetime, datetime], filters: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate financial data for reporting"""
        try:
            start_date, end_date = date_range
            
            # Get financial transactions
            query = {
                "date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
            
            if filters.get("account_id"):
                query["account_id"] = filters["account_id"]
            
            transactions = await self.db.financial_transactions.find(query).to_list(length=None)
            
            if not transactions:
                return pd.DataFrame()
            
            df = pd.DataFrame(transactions)
            
            # Calculate financial metrics
            df["net_revenue"] = df["revenue"] - df["costs"]
            df["profit_margin"] = df["net_revenue"] / df["revenue"]
            
            return df
            
        except Exception as e:
            logger.error(f"Error aggregating financial data: {e}")
            return pd.DataFrame()
    
    async def aggregate_audience_data(self, date_range: Tuple[datetime, datetime], filters: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate audience data for reporting"""
        try:
            start_date, end_date = date_range
            
            # Get audience data
            query = {
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
            
            if filters.get("segment_id"):
                query["segment_id"] = filters["segment_id"]
            
            audience_data = await self.db.audience_analytics.find(query).to_list(length=None)
            
            if not audience_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(audience_data)
            
            # Calculate audience metrics
            df["engagement_rate"] = df["engagements"] / df["reach"]
            df["growth_rate"] = df["new_followers"] / df["total_followers"]
            
            return df
            
        except Exception as e:
            logger.error(f"Error aggregating audience data: {e}")
            return pd.DataFrame()

class ChartGenerator:
    """Generates various types of charts for reports"""
    
    def __init__(self):
        self.chart_templates = self._initialize_chart_templates()
    
    def _initialize_chart_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize chart templates"""
        return {
            "line": {
                "template": go.Scatter,
                "default_config": {
                    "mode": "lines+markers",
                    "line": {"width": 3},
                    "marker": {"size": 8}
                }
            },
            "bar": {
                "template": go.Bar,
                "default_config": {
                    "marker": {"color": "lightblue"}
                }
            },
            "pie": {
                "template": go.Pie,
                "default_config": {
                    "textposition": "inside",
                    "textinfo": "percent+label"
                }
            },
            "scatter": {
                "template": go.Scatter,
                "default_config": {
                    "mode": "markers",
                    "marker": {"size": 12}
                }
            },
            "area": {
                "template": go.Scatter,
                "default_config": {
                    "mode": "lines",
                    "fill": "tonexty"
                }
            },
            "heatmap": {
                "template": go.Heatmap,
                "default_config": {
                    "colorscale": "Viridis"
                }
            },
            "funnel": {
                "template": go.Funnel,
                "default_config": {
                    "marker": {"color": "lightcoral"}
                }
            },
            "gauge": {
                "template": go.Indicator,
                "default_config": {
                    "mode": "gauge+number+delta",
                    "gauge": {"axis": {"range": [None, 100]}}
                }
            }
        }
    
    def generate_line_chart(self, data: pd.DataFrame, x_col: str, y_col: str, title: str, config: Dict[str, Any] = None) -> str:
        """Generate line chart"""
        try:
            config = config or {}
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data[x_col],
                y=data[y_col],
                mode="lines+markers",
                name=y_col,
                line=config.get("line", {"width": 3}),
                marker=config.get("marker", {"size": 8})
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating line chart: {e}")
            return ""
    
    def generate_bar_chart(self, data: pd.DataFrame, x_col: str, y_col: str, title: str, config: Dict[str, Any] = None) -> str:
        """Generate bar chart"""
        try:
            config = config or {}
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=data[x_col],
                y=data[y_col],
                name=y_col,
                marker=config.get("marker", {"color": "lightblue"})
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating bar chart: {e}")
            return ""
    
    def generate_pie_chart(self, data: pd.DataFrame, labels_col: str, values_col: str, title: str, config: Dict[str, Any] = None) -> str:
        """Generate pie chart"""
        try:
            config = config or {}
            
            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=data[labels_col],
                values=data[values_col],
                textposition=config.get("textposition", "inside"),
                textinfo=config.get("textinfo", "percent+label")
            ))
            
            fig.update_layout(
                title=title,
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating pie chart: {e}")
            return ""
    
    def generate_heatmap(self, data: pd.DataFrame, x_col: str, y_col: str, z_col: str, title: str, config: Dict[str, Any] = None) -> str:
        """Generate heatmap"""
        try:
            config = config or {}
            
            # Pivot data for heatmap
            pivot_data = data.pivot_table(values=z_col, index=y_col, columns=x_col, aggfunc='mean')
            
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                colorscale=config.get("colorscale", "Viridis")
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating heatmap: {e}")
            return ""
    
    def generate_funnel_chart(self, data: pd.DataFrame, stage_col: str, value_col: str, title: str, config: Dict[str, Any] = None) -> str:
        """Generate funnel chart"""
        try:
            config = config or {}
            
            fig = go.Figure()
            fig.add_trace(go.Funnel(
                y=data[stage_col],
                x=data[value_col],
                marker=config.get("marker", {"color": "lightcoral"})
            ))
            
            fig.update_layout(
                title=title,
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating funnel chart: {e}")
            return ""
    
    def generate_gauge_chart(self, value: float, title: str, config: Dict[str, Any] = None) -> str:
        """Generate gauge chart"""
        try:
            config = config or {}
            
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                title={"text": title},
                gauge={
                    "axis": {"range": config.get("range", [None, 100])},
                    "bar": {"color": "darkblue"},
                    "steps": config.get("steps", []),
                    "threshold": config.get("threshold", {})
                }
            ))
            
            fig.update_layout(
                template="plotly_white",
                **config.get("layout", {})
            )
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Error generating gauge chart: {e}")
            return ""

class ReportGenerator:
    """Generates reports in various formats"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.data_aggregator = DataAggregator(db)
        self.chart_generator = ChartGenerator()
        self.template_env = jinja2.Environment(loader=jinja2.DictLoader({}))
    
    async def generate_campaign_performance_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate campaign performance report"""
        try:
            # Parse parameters
            start_date = datetime.fromisoformat(parameters["start_date"])
            end_date = datetime.fromisoformat(parameters["end_date"])
            filters = parameters.get("filters", {})
            
            # Aggregate data
            campaign_data = await self.data_aggregator.aggregate_campaign_data((start_date, end_date), filters)
            
            if campaign_data.empty:
                return {"error": "No data available for the specified period"}
            
            # Generate charts
            charts = {}
            
            # ROAS over time
            if "date" in campaign_data.columns and "roas" in campaign_data.columns:
                charts["roas_trend"] = self.chart_generator.generate_line_chart(
                    campaign_data, "date", "roas", "ROAS Trend"
                )
            
            # Campaign performance by platform
            if "platform" in campaign_data.columns and "spend" in campaign_data.columns:
                platform_performance = campaign_data.groupby("platform")["spend"].sum().reset_index()
                charts["platform_performance"] = self.chart_generator.generate_bar_chart(
                    platform_performance, "platform", "spend", "Spend by Platform"
                )
            
            # Conversion funnel
            if "impressions" in campaign_data.columns and "clicks" in campaign_data.columns and "conversions" in campaign_data.columns:
                funnel_data = pd.DataFrame({
                    "stage": ["Impressions", "Clicks", "Conversions"],
                    "value": [
                        campaign_data["impressions"].sum(),
                        campaign_data["clicks"].sum(),
                        campaign_data["conversions"].sum()
                    ]
                })
                charts["conversion_funnel"] = self.chart_generator.generate_funnel_chart(
                    funnel_data, "stage", "value", "Conversion Funnel"
                )
            
            # Calculate summary metrics
            summary_metrics = {
                "total_spend": campaign_data["spend"].sum(),
                "total_revenue": campaign_data["revenue"].sum(),
                "total_conversions": campaign_data["conversions"].sum(),
                "average_roas": campaign_data["roas"].mean(),
                "average_cpa": campaign_data["cpa"].mean(),
                "total_impressions": campaign_data["impressions"].sum(),
                "total_clicks": campaign_data["clicks"].sum(),
                "average_ctr": campaign_data["ctr"].mean()
            }
            
            return {
                "report_type": "campaign_performance",
                "summary_metrics": summary_metrics,
                "charts": charts,
                "data_points": len(campaign_data),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating campaign performance report: {e}")
            raise
    
    async def generate_financial_summary_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial summary report"""
        try:
            # Parse parameters
            start_date = datetime.fromisoformat(parameters["start_date"])
            end_date = datetime.fromisoformat(parameters["end_date"])
            filters = parameters.get("filters", {})
            
            # Aggregate data
            financial_data = await self.data_aggregator.aggregate_financial_data((start_date, end_date), filters)
            
            if financial_data.empty:
                return {"error": "No financial data available for the specified period"}
            
            # Generate charts
            charts = {}
            
            # Revenue trend
            if "date" in financial_data.columns and "revenue" in financial_data.columns:
                charts["revenue_trend"] = self.chart_generator.generate_line_chart(
                    financial_data, "date", "revenue", "Revenue Trend"
                )
            
            # Profit margin gauge
            if "profit_margin" in financial_data.columns:
                avg_profit_margin = financial_data["profit_margin"].mean() * 100
                charts["profit_margin_gauge"] = self.chart_generator.generate_gauge_chart(
                    avg_profit_margin, "Average Profit Margin (%)"
                )
            
            # Revenue by category
            if "category" in financial_data.columns and "revenue" in financial_data.columns:
                category_revenue = financial_data.groupby("category")["revenue"].sum().reset_index()
                charts["revenue_by_category"] = self.chart_generator.generate_pie_chart(
                    category_revenue, "category", "revenue", "Revenue by Category"
                )
            
            # Calculate summary metrics
            summary_metrics = {
                "total_revenue": financial_data["revenue"].sum(),
                "total_costs": financial_data["costs"].sum(),
                "net_revenue": financial_data["net_revenue"].sum(),
                "average_profit_margin": financial_data["profit_margin"].mean(),
                "transaction_count": len(financial_data)
            }
            
            return {
                "report_type": "financial_summary",
                "summary_metrics": summary_metrics,
                "charts": charts,
                "data_points": len(financial_data),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating financial summary report: {e}")
            raise
    
    async def generate_executive_summary_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            # Parse parameters
            start_date = datetime.fromisoformat(parameters["start_date"])
            end_date = datetime.fromisoformat(parameters["end_date"])
            
            # Get all data types
            campaign_data = await self.data_aggregator.aggregate_campaign_data((start_date, end_date), {})
            financial_data = await self.data_aggregator.aggregate_financial_data((start_date, end_date), {})
            audience_data = await self.data_aggregator.aggregate_audience_data((start_date, end_date), {})
            
            # Generate key performance indicators
            kpis = {}
            
            if not campaign_data.empty:
                kpis["campaign_performance"] = {
                    "total_spend": campaign_data["spend"].sum(),
                    "total_revenue": campaign_data["revenue"].sum(),
                    "average_roas": campaign_data["roas"].mean(),
                    "total_conversions": campaign_data["conversions"].sum()
                }
            
            if not financial_data.empty:
                kpis["financial_performance"] = {
                    "total_revenue": financial_data["revenue"].sum(),
                    "net_revenue": financial_data["net_revenue"].sum(),
                    "profit_margin": financial_data["profit_margin"].mean()
                }
            
            if not audience_data.empty:
                kpis["audience_performance"] = {
                    "total_reach": audience_data["reach"].sum(),
                    "total_engagements": audience_data["engagements"].sum(),
                    "average_engagement_rate": audience_data["engagement_rate"].mean()
                }
            
            # Generate executive charts
            charts = {}
            
            # Overall performance gauge
            if kpis.get("campaign_performance", {}).get("average_roas"):
                roas_percentage = kpis["campaign_performance"]["average_roas"] * 100
                charts["overall_performance"] = self.chart_generator.generate_gauge_chart(
                    roas_percentage, "Overall ROAS Performance"
                )
            
            # Revenue vs Spend trend
            if not campaign_data.empty and "date" in campaign_data.columns:
                daily_data = campaign_data.groupby("date").agg({
                    "revenue": "sum",
                    "spend": "sum"
                }).reset_index()
                
                charts["revenue_vs_spend"] = self.chart_generator.generate_line_chart(
                    daily_data, "date", "revenue", "Revenue vs Spend Trend"
                )
            
            return {
                "report_type": "executive_summary",
                "kpis": kpis,
                "charts": charts,
                "insights": self._generate_executive_insights(kpis),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating executive summary report: {e}")
            raise
    
    def _generate_executive_insights(self, kpis: Dict[str, Any]) -> List[str]:
        """Generate executive insights from KPIs"""
        insights = []
        
        campaign_kpis = kpis.get("campaign_performance", {})
        financial_kpis = kpis.get("financial_performance", {})
        audience_kpis = kpis.get("audience_performance", {})
        
        if campaign_kpis.get("average_roas", 0) > 3.0:
            insights.append("Excellent ROAS performance indicates strong campaign effectiveness")
        elif campaign_kpis.get("average_roas", 0) > 2.0:
            insights.append("Good ROAS performance with room for optimization")
        else:
            insights.append("ROAS performance needs improvement - consider campaign optimization")
        
        if financial_kpis.get("profit_margin", 0) > 0.2:
            insights.append("Strong profit margins indicate healthy business performance")
        elif financial_kpis.get("profit_margin", 0) > 0.1:
            insights.append("Moderate profit margins - consider cost optimization")
        else:
            insights.append("Low profit margins require immediate attention")
        
        if audience_kpis.get("average_engagement_rate", 0) > 0.05:
            insights.append("High audience engagement indicates strong brand connection")
        elif audience_kpis.get("average_engagement_rate", 0) > 0.02:
            insights.append("Moderate audience engagement - consider content optimization")
        else:
            insights.append("Low audience engagement - review content strategy")
        
        return insights

class ReportExporter:
    """Exports reports in various formats"""
    
    def __init__(self):
        self.template_env = jinja2.Environment(loader=jinja2.DictLoader({}))
    
    async def export_to_pdf(self, report_data: Dict[str, Any], template: str) -> bytes:
        """Export report to PDF"""
        try:
            # Render HTML template
            html_template = self.template_env.from_string(template)
            html_content = html_template.render(report_data)
            
            # Generate PDF
            pdf_bytes = HTML(string=html_content).write_pdf()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise
    
    async def export_to_excel(self, report_data: Dict[str, Any]) -> bytes:
        """Export report to Excel"""
        try:
            # Create Excel file in memory
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write summary metrics
                if "summary_metrics" in report_data:
                    metrics_df = pd.DataFrame([report_data["summary_metrics"]])
                    metrics_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Write KPIs
                if "kpis" in report_data:
                    for kpi_name, kpi_data in report_data["kpis"].items():
                        kpi_df = pd.DataFrame([kpi_data])
                        kpi_df.to_excel(writer, sheet_name=kpi_name.title(), index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    async def export_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Export report to CSV"""
        try:
            # Convert report data to CSV format
            csv_data = []
            
            if "summary_metrics" in report_data:
                csv_data.append("Metric,Value")
                for metric, value in report_data["summary_metrics"].items():
                    csv_data.append(f"{metric},{value}")
            
            return "\n".join(csv_data)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise

class AdvancedReportingService:
    """Main service for advanced reporting and BI"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.report_generator = ReportGenerator(db)
        self.report_exporter = ReportExporter()
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize report templates"""
        self.templates = {
            ReportType.CAMPAIGN_PERFORMANCE: {
                "name": "Campaign Performance Report",
                "description": "Comprehensive campaign performance analysis",
                "chart_configs": [
                    {"type": "line", "title": "ROAS Trend", "x": "date", "y": "roas"},
                    {"type": "bar", "title": "Spend by Platform", "x": "platform", "y": "spend"},
                    {"type": "funnel", "title": "Conversion Funnel", "stage": "stage", "value": "value"}
                ]
            },
            ReportType.FINANCIAL_SUMMARY: {
                "name": "Financial Summary Report",
                "description": "Financial performance and profitability analysis",
                "chart_configs": [
                    {"type": "line", "title": "Revenue Trend", "x": "date", "y": "revenue"},
                    {"type": "gauge", "title": "Profit Margin", "value": "profit_margin"},
                    {"type": "pie", "title": "Revenue by Category", "labels": "category", "values": "revenue"}
                ]
            },
            ReportType.EXECUTIVE_SUMMARY: {
                "name": "Executive Summary Report",
                "description": "High-level performance overview for executives",
                "chart_configs": [
                    {"type": "gauge", "title": "Overall Performance", "value": "roas"},
                    {"type": "line", "title": "Revenue vs Spend", "x": "date", "y": "revenue"}
                ]
            }
        }
    
    async def create_report_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new report template"""
        try:
            template_id = str(uuid.uuid4())
            
            template = ReportTemplate(
                template_id=template_id,
                name=template_data["name"],
                description=template_data.get("description", ""),
                report_type=ReportType(template_data["report_type"]),
                chart_configs=template_data.get("chart_configs", []),
                filters=template_data.get("filters", []),
                layout=template_data.get("layout", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save template to database
            template_doc = {
                "template_id": template_id,
                "name": template.name,
                "description": template.description,
                "report_type": template.report_type.value,
                "chart_configs": template.chart_configs,
                "filters": template.filters,
                "layout": template.layout,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            }
            
            await self.db.report_templates.insert_one(template_doc)
            
            logger.info(f"Created report template {template_id}: {template.name}")
            return template_id
            
        except Exception as e:
            logger.error(f"Error creating report template: {e}")
            raise
    
    async def generate_report(self, template_id: str, parameters: Dict[str, Any], created_by: str) -> str:
        """Generate a report from template"""
        try:
            report_id = str(uuid.uuid4())
            
            # Get template
            template_doc = await self.db.report_templates.find_one({"template_id": template_id})
            if not template_doc:
                raise ValueError(f"Template {template_id} not found")
            
            # Create report instance
            report_instance = ReportInstance(
                report_id=report_id,
                template_id=template_id,
                name=f"{template_doc['name']} - {datetime.utcnow().strftime('%Y-%m-%d')}",
                status=ReportStatus.GENERATING,
                parameters=parameters,
                generated_at=None,
                file_path=None,
                file_size=None,
                created_by=created_by,
                created_at=datetime.utcnow()
            )
            
            # Save report instance
            report_doc = {
                "report_id": report_id,
                "template_id": template_id,
                "name": report_instance.name,
                "status": report_instance.status.value,
                "parameters": parameters,
                "generated_at": None,
                "file_path": None,
                "file_size": None,
                "created_by": created_by,
                "created_at": report_instance.created_at.isoformat()
            }
            
            await self.db.reports.insert_one(report_doc)
            
            # Generate report asynchronously
            asyncio.create_task(self._generate_report_async(report_id, template_doc, parameters))
            
            logger.info(f"Started generating report {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _generate_report_async(self, report_id: str, template_doc: Dict[str, Any], parameters: Dict[str, Any]):
        """Generate report asynchronously"""
        try:
            report_type = ReportType(template_doc["report_type"])
            
            # Generate report data based on type
            if report_type == ReportType.CAMPAIGN_PERFORMANCE:
                report_data = await self.report_generator.generate_campaign_performance_report(parameters)
            elif report_type == ReportType.FINANCIAL_SUMMARY:
                report_data = await self.report_generator.generate_financial_summary_report(parameters)
            elif report_type == ReportType.EXECUTIVE_SUMMARY:
                report_data = await self.report_generator.generate_executive_summary_report(parameters)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Update report status
            await self.db.reports.update_one(
                {"report_id": report_id},
                {
                    "$set": {
                        "status": ReportStatus.COMPLETED.value,
                        "generated_at": datetime.utcnow().isoformat(),
                        "report_data": report_data
                    }
                }
            )
            
            logger.info(f"Completed generating report {report_id}")
            
        except Exception as e:
            logger.error(f"Error in async report generation: {e}")
            await self.db.reports.update_one(
                {"report_id": report_id},
                {
                    "$set": {
                        "status": ReportStatus.FAILED.value,
                        "error_message": str(e)
                    }
                }
            )
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """Get generated report"""
        try:
            report_doc = await self.db.reports.find_one({"report_id": report_id})
            if not report_doc:
                raise ValueError(f"Report {report_id} not found")
            
            return report_doc
            
        except Exception as e:
            logger.error(f"Error getting report: {e}")
            raise
    
    async def export_report(self, report_id: str, format: ReportFormat) -> bytes:
        """Export report in specified format"""
        try:
            report_doc = await self.get_report(report_id)
            
            if report_doc["status"] != ReportStatus.COMPLETED.value:
                raise ValueError("Report not completed yet")
            
            report_data = report_doc.get("report_data", {})
            
            if format == ReportFormat.PDF:
                template = self._get_pdf_template(report_doc["template_id"])
                return await self.report_exporter.export_to_pdf(report_data, template)
            elif format == ReportFormat.EXCEL:
                return await self.report_exporter.export_to_excel(report_data)
            elif format == ReportFormat.CSV:
                csv_content = await self.report_exporter.export_to_csv(report_data)
                return csv_content.encode('utf-8')
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise
    
    def _get_pdf_template(self, template_id: str) -> str:
        """Get PDF template for report"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ report_type }} Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .summary { margin-bottom: 30px; }
                .chart { margin-bottom: 30px; text-align: center; }
                .metric { display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ report_type }} Report</h1>
                <p>Generated on {{ date_range.start }} to {{ date_range.end }}</p>
            </div>
            
            {% if summary_metrics %}
            <div class="summary">
                <h2>Summary Metrics</h2>
                {% for metric, value in summary_metrics.items() %}
                <div class="metric">
                    <strong>{{ metric }}</strong>: {{ value }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if insights %}
            <div class="insights">
                <h2>Key Insights</h2>
                <ul>
                {% for insight in insights %}
                <li>{{ insight }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </body>
        </html>
        """
    
    async def get_reporting_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive reporting dashboard"""
        try:
            # Get report statistics
            total_reports = await self.db.reports.count_documents({})
            completed_reports = await self.db.reports.count_documents({"status": ReportStatus.COMPLETED.value})
            failed_reports = await self.db.reports.count_documents({"status": ReportStatus.FAILED.value})
            
            # Get template statistics
            total_templates = await self.db.report_templates.count_documents({})
            
            # Get recent reports
            recent_reports = await self.db.reports.find({}).sort("created_at", -1).limit(10).to_list(length=None)
            
            return {
                "organization_id": organization_id,
                "report_statistics": {
                    "total_reports": total_reports,
                    "completed_reports": completed_reports,
                    "failed_reports": failed_reports,
                    "success_rate": completed_reports / total_reports if total_reports > 0 else 0
                },
                "template_statistics": {
                    "total_templates": total_templates
                },
                "recent_reports": recent_reports,
                "supported_formats": [format.value for format in ReportFormat],
                "supported_chart_types": [chart_type.value for chart_type in ChartType],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting reporting dashboard: {e}")
            raise

# Global instance
advanced_reporting_service = None

def get_advanced_reporting_service(db: AsyncIOMotorClient) -> AdvancedReportingService:
    """Get advanced reporting service instance"""
    global advanced_reporting_service
    if advanced_reporting_service is None:
        advanced_reporting_service = AdvancedReportingService(db)
    return advanced_reporting_service
