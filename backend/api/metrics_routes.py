"""
Prometheus Metrics Endpoint
"""

from fastapi import APIRouter
from fastapi.responses import Response
from services.prometheus_metrics import metrics_collector

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    metrics_data = metrics_collector.get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

