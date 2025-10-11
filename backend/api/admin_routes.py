"""
Admin API Routes for OmnifyProduct
Provides administrative endpoints for system monitoring and client support
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.log_analysis_service import get_log_analysis_service
from services.structured_logging import logger

router = APIRouter(prefix="/api/admin", tags=["admin"])

async def get_database(db: AsyncIOMotorDatabase = Depends()) -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return db

@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query("ALL", description="Log level filter"),
    timeRange: Optional[str] = Query("1h", description="Time range (5m, 1h, 24h, 7d, 30d)"),
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    organizationId: Optional[str] = Query(None, description="Filter by organization ID"),
    workflowId: Optional[str] = Query(None, description="Filter by workflow ID"),
    eventType: Optional[str] = Query(None, description="Filter by event type"),
    search: Optional[str] = Query(None, description="Search in messages and IDs"),
    limit: Optional[int] = Query(1000, description="Maximum logs to return"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get filtered logs with analysis

    - **level**: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - **timeRange**: Time range for logs
    - **userId**: Filter logs for specific user
    - **organizationId**: Filter logs for specific organization
    - **workflowId**: Filter logs for specific workflow
    - **eventType**: Filter by event type (errors, workflows, api, etc.)
    - **search**: Search in log messages and IDs
    - **limit**: Maximum number of logs to return
    """
    try:
        log_service = get_log_analysis_service(db)

        filters = {
            'level': level,
            'timeRange': timeRange,
            'userId': userId,
            'organizationId': organizationId,
            'workflowId': workflowId,
            'eventType': eventType,
            'search': search,
            'limit': limit
        }

        result = await log_service.get_logs(filters)

        logger.info(
            f"Admin logs query executed",
            event_type='admin_logs_query',
            filters_applied=filters,
            logs_returned=len(result.get('logs', []))
        )

        return result

    except Exception as e:
        logger.error(f"Failed to retrieve admin logs: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@router.post("/client-support")
async def analyze_client_issue(
    request: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Analyze client issue from logs and provide recommendations

    **Request Body:**
    - **clientId**: User ID or Organization ID to analyze
    - **issueDescription**: Description of the reported issue
    """
    try:
        client_id = request.get('clientId')
        issue_description = request.get('issueDescription')

        if not client_id:
            raise HTTPException(status_code=400, detail="clientId is required")
        if not issue_description:
            raise HTTPException(status_code=400, detail="issueDescription is required")

        log_service = get_log_analysis_service(db)
        analysis = await log_service.analyze_client_issue(client_id, issue_description)

        logger.info(
            f"Client issue analysis completed for {client_id}",
            event_type='client_support_analysis',
            client_id=client_id,
            logs_analyzed=analysis.get('total_logs', 0)
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze client issue: {str(e)}",
                    client_id=request.get('clientId'), exc_info=e)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/system-health")
async def get_system_health(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Get overall system health metrics
    """
    try:
        log_service = get_log_analysis_service(db)

        # Get recent logs for health analysis
        recent_logs = await log_service.get_logs({
            'timeRange': '1h',
            'limit': 10000
        })

        logs = recent_logs.get('logs', [])
        analysis = recent_logs.get('analysis', {})

        # Calculate health metrics
        health_metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'metrics': {
                'total_logs_last_hour': len(logs),
                'error_rate': analysis.get('summary', {}).get('error_rate', 0),
                'avg_response_time': analysis.get('performance', {}).get('avg_response_time'),
                'active_workflows': analysis.get('workflows', {}).get('unique_workflows', 0),
                'completed_workflows': analysis.get('workflows', {}).get('completed_workflows', 0)
            },
            'alerts': []
        }

        # Determine overall status
        error_rate = health_metrics['metrics']['error_rate']
        if error_rate > 0.1:  # > 10% errors
            health_metrics['overall_status'] = 'critical'
            health_metrics['alerts'].append('High error rate detected')
        elif error_rate > 0.05:  # > 5% errors
            health_metrics['overall_status'] = 'warning'
            health_metrics['alerts'].append('Elevated error rate')

        avg_response_time = health_metrics['metrics']['avg_response_time']
        if avg_response_time and avg_response_time > 5000:  # > 5 seconds
            health_metrics['overall_status'] = 'warning'
            health_metrics['alerts'].append('Slow average response time')

        if not health_metrics['alerts']:
            health_metrics['overall_status'] = 'healthy'

        logger.info(
            f"System health check completed",
            event_type='system_health_check',
            status=health_metrics['overall_status'],
            error_rate=error_rate,
            avg_response_time=avg_response_time
        )

        return health_metrics

    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}", exc_info=e)
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'unknown',
            'error': str(e)
        }

@router.get("/workflow-stats")
async def get_workflow_stats(
    timeRange: Optional[str] = Query("24h", description="Time range for analysis"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get comprehensive workflow statistics
    """
    try:
        log_service = get_log_analysis_service(db)

        # Get workflow-related logs
        workflow_logs = await log_service.get_logs({
            'eventType': 'workflows',
            'timeRange': timeRange,
            'limit': 10000
        })

        analysis = workflow_logs.get('analysis', {}).get('workflows', {})

        # Enhanced workflow statistics
        stats = {
            'time_range': timeRange,
            'total_workflow_events': analysis.get('total_workflow_events', 0),
            'unique_workflows': analysis.get('unique_workflows', 0),
            'completed_workflows': analysis.get('completed_workflows', 0),
            'error_workflows': analysis.get('error_workflows', 0),
            'success_rate': 0,
            'avg_completion_time': None,
            'most_active_workflows': [],
            'error_patterns': []
        }

        # Calculate success rate
        total_completed = stats['completed_workflows'] + stats['error_workflows']
        if total_completed > 0:
            stats['success_rate'] = (stats['completed_workflows'] / total_completed) * 100

        # Calculate average completion time
        workflow_stats = analysis.get('workflow_stats', {})
        completion_times = [
            wf_stat['duration_seconds']
            for wf_stat in workflow_stats.values()
            if wf_stat.get('duration_seconds') and wf_stat['status'] == 'completed'
        ]
        if completion_times:
            stats['avg_completion_time'] = sum(completion_times) / len(completion_times)

        # Most active workflows
        workflow_counts = Counter()
        for wf_id, wf_stat in workflow_stats.items():
            workflow_counts[wf_id] = wf_stat['events_count']
        stats['most_active_workflows'] = workflow_counts.most_common(5)

        logger.info(
            f"Workflow statistics generated",
            event_type='workflow_stats_generated',
            time_range=timeRange,
            workflows_analyzed=stats['unique_workflows']
        )

        return stats

    except Exception as e:
        logger.error(f"Failed to get workflow stats: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Failed to get workflow stats: {str(e)}")

@router.get("/performance-metrics")
async def get_performance_metrics(
    timeRange: Optional[str] = Query("1h", description="Time range for analysis"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed performance metrics
    """
    try:
        log_service = get_log_analysis_service(db)

        # Get API performance logs
        api_logs = await log_service.get_logs({
            'eventType': 'api',
            'timeRange': timeRange,
            'limit': 10000
        })

        analysis = api_logs.get('analysis', {}).get('performance', {})

        # Enhanced performance metrics
        metrics = {
            'time_range': timeRange,
            'total_requests': analysis.get('total_requests', 0),
            'avg_response_time': analysis.get('avg_response_time'),
            'max_response_time': analysis.get('max_response_time'),
            'min_response_time': analysis.get('min_response_time'),
            'slow_requests': analysis.get('slow_requests', 0),
            'status_codes': analysis.get('status_codes', {}),
            'top_endpoints': analysis.get('top_endpoints', {}),
            'performance_trends': [],
            'bottlenecks': []
        }

        # Identify bottlenecks
        if metrics['slow_requests'] > 0:
            metrics['bottlenecks'].append({
                'type': 'slow_requests',
                'count': metrics['slow_requests'],
                'recommendation': 'Review database queries and external API calls'
            })

        if metrics['avg_response_time'] and metrics['avg_response_time'] > 2000:
            metrics['bottlenecks'].append({
                'type': 'high_avg_response',
                'avg_time': metrics['avg_response_time'],
                'recommendation': 'Optimize API endpoints and caching'
            })

        # Check for error rates in status codes
        error_codes = {k: v for k, v in metrics['status_codes'].items() if str(k).startswith(('4', '5'))}
        if error_codes:
            metrics['bottlenecks'].append({
                'type': 'high_error_rate',
                'error_codes': error_codes,
                'recommendation': 'Review error handling and validation'
            })

        logger.info(
            f"Performance metrics generated",
            event_type='performance_metrics_generated',
            time_range=timeRange,
            requests_analyzed=metrics['total_requests']
        )

        return metrics

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

# Import here to avoid circular imports
from datetime import datetime
