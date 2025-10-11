"""
Log Analysis Service for OmnifyProduct
Provides comprehensive log analysis and client support features
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import re
from collections import defaultdict, Counter
from services.structured_logging import logger

class LogAnalysisService:
    """
    Service for analyzing logs and providing insights for admin dashboard
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_logs(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get filtered logs with advanced analysis
        """
        try:
            query = self._build_query(filters)
            sort_order = [("timestamp", -1)]  # Most recent first
            limit = min(filters.get('limit', 1000), 5000)  # Cap at 5000

            # Get logs
            logs_cursor = self.db.logs.find(query).sort(sort_order).limit(limit)
            logs = await logs_cursor.to_list(length=None)

            # Add analysis
            analysis = await self._analyze_logs(logs, filters)

            return {
                'logs': logs,
                'analysis': analysis,
                'total_count': len(logs),
                'filters_applied': filters
            }

        except Exception as e:
            logger.error(f"Failed to get logs: {str(e)}", exc_info=e)
            return {
                'logs': [],
                'analysis': {},
                'error': str(e)
            }

    async def analyze_client_issue(self, client_id: str, issue_description: str) -> Dict[str, Any]:
        """
        Comprehensive client issue analysis
        """
        try:
            # Get recent logs for client (last 24 hours)
            time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()

            client_logs = await self.db.logs.find({
                'timestamp': {'$gte': time_threshold},
                '$or': [
                    {'context.user_id': client_id},
                    {'context.organization_id': client_id}
                ]
            }).sort('timestamp', -1).to_list(200)

            # Analyze the logs
            analysis = {
                'client_id': client_id,
                'issue_description': issue_description,
                'analysis_period': '24 hours',
                'total_logs': len(client_logs),
                'log_summary': self._summarize_logs(client_logs),
                'error_analysis': self._analyze_errors(client_logs),
                'workflow_analysis': self._analyze_workflows(client_logs),
                'performance_analysis': self._analyze_performance(client_logs),
                'recommendations': self._generate_recommendations(client_logs, issue_description),
                'critical_findings': self._identify_critical_issues(client_logs),
                'recent_logs': client_logs[:20]  # Last 20 logs
            }

            logger.info(f"Client issue analysis completed for {client_id}",
                       event_type='client_analysis_complete',
                       client_id=client_id,
                       logs_analyzed=len(client_logs))

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze client issue: {str(e)}",
                        client_id=client_id, exc_info=e)
            return {
                'client_id': client_id,
                'error': f"Analysis failed: {str(e)}"
            }

    def _build_query(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build MongoDB query from filters"""
        query = {}

        # Level filter
        if filters.get('level') and filters['level'] != 'ALL':
            query['level'] = filters['level']

        # Time range filter
        if filters.get('timeRange'):
            hours_map = {
                '5m': 0.083, '15m': 0.25, '1h': 1, '6h': 6,
                '24h': 24, '7d': 168, '30d': 720
            }
            hours = hours_map.get(filters['timeRange'], 1)
            since = datetime.utcnow() - timedelta(hours=hours)
            query['timestamp'] = {'$gte': since.isoformat()}

        # User filter
        if filters.get('userId'):
            query['context.user_id'] = filters['userId']

        # Organization filter
        if filters.get('organizationId'):
            query['context.organization_id'] = filters['organizationId']

        # Workflow filter
        if filters.get('workflowId'):
            query['context.workflow_id'] = filters['workflowId']

        # Event type filter
        if filters.get('eventType'):
            if filters['eventType'] == 'errors':
                query['level'] = 'ERROR'
            elif filters['eventType'] == 'workflows':
                query['event_type'] = {'$regex': '^workflow'}
            elif filters['eventType'] == 'api':
                query['event_type'] = {'$regex': '^request|^api'}
            else:
                query['event_type'] = filters['eventType']

        # Search filter
        if filters.get('search'):
            search_regex = re.compile(filters['search'], re.IGNORECASE)
            query['$or'] = [
                {'message': search_regex},
                {'context.workflow_id': search_regex},
                {'context.user_id': search_regex},
                {'event_type': search_regex}
            ]

        return query

    def _summarize_logs(self, logs: List[Dict]) -> Dict[str, Any]:
        """Create summary statistics of logs"""
        if not logs:
            return {'total': 0}

        levels = Counter(log.get('level') for log in logs)
        event_types = Counter(log.get('event_type') for log in logs if log.get('event_type'))

        # Time range
        timestamps = [log.get('timestamp') for log in logs if log.get('timestamp')]
        if timestamps:
            timestamps.sort()
            time_span = (
                datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00')) -
                datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))
            ).total_seconds() / 3600  # hours
        else:
            time_span = 0

        return {
            'total': len(logs),
            'time_span_hours': round(time_span, 2),
            'levels': dict(levels),
            'event_types': dict(event_types.most_common(10)),
            'error_rate': levels.get('ERROR', 0) / len(logs) if logs else 0
        }

    def _analyze_errors(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns"""
        errors = [log for log in logs if log.get('level') == 'ERROR']

        if not errors:
            return {'total_errors': 0, 'error_rate': 0}

        # Error messages frequency
        error_messages = Counter()
        error_types = Counter()
        error_contexts = defaultdict(list)

        for error in errors:
            message = error.get('message', '')
            # Extract error type from message
            if ':' in message:
                error_type = message.split(':')[0].strip()
            else:
                error_type = message[:50]

            error_messages[message] += 1
            error_types[error_type] += 1

            # Group by context
            workflow_id = error.get('context', {}).get('workflow_id')
            if workflow_id:
                error_contexts[workflow_id].append(error)

        return {
            'total_errors': len(errors),
            'error_rate': len(errors) / len(logs) if logs else 0,
            'top_error_messages': dict(error_messages.most_common(5)),
            'error_types': dict(error_types.most_common(5)),
            'errors_by_workflow': {
                wf_id: len(errors) for wf_id, errors in error_contexts.items()
            }
        }

    def _analyze_workflows(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze workflow execution patterns"""
        workflow_events = [log for log in logs if log.get('event_type', '').startswith('workflow')]

        if not workflow_events:
            return {'total_workflow_events': 0}

        # Group by workflow
        workflows = defaultdict(list)
        for event in workflow_events:
            wf_id = event.get('context', {}).get('workflow_id')
            if wf_id:
                workflows[wf_id].append(event)

        workflow_stats = {}
        for wf_id, events in workflows.items():
            # Sort by timestamp
            events.sort(key=lambda x: x.get('timestamp', ''))

            start_time = None
            end_time = None
            has_error = False
            steps_completed = 0

            for event in events:
                event_type = event.get('event_type')

                if event_type == 'workflow_start':
                    start_time = event.get('timestamp')
                elif event_type == 'workflow_complete':
                    end_time = event.get('timestamp')
                elif event_type == 'workflow_error':
                    has_error = True
                elif event_type == 'workflow_step':
                    if event.get('step_status') == 'completed':
                        steps_completed += 1

            duration = None
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end_dt - start_dt).total_seconds()
                except:
                    pass

            workflow_stats[wf_id] = {
                'events_count': len(events),
                'has_error': has_error,
                'steps_completed': steps_completed,
                'duration_seconds': duration,
                'status': 'error' if has_error else ('completed' if end_time else 'running')
            }

        return {
            'total_workflow_events': len(workflow_events),
            'unique_workflows': len(workflows),
            'workflow_stats': workflow_stats,
            'error_workflows': sum(1 for stats in workflow_stats.values() if stats['has_error']),
            'completed_workflows': sum(1 for stats in workflow_stats.values() if stats['status'] == 'completed')
        }

    def _analyze_performance(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze performance metrics"""
        request_events = [log for log in logs if log.get('event_type') in ['request_complete', 'request_error']]

        if not request_events:
            return {'total_requests': 0}

        durations = []
        status_codes = Counter()
        endpoints = Counter()

        for event in request_events:
            # Duration
            if 'duration_ms' in event:
                durations.append(event['duration_ms'])

            # Status codes
            if 'status_code' in event:
                status_codes[event['status_code']] += 1

            # Endpoints
            if 'path' in event:
                endpoints[event['path']] += 1

        return {
            'total_requests': len(request_events),
            'avg_response_time': round(sum(durations) / len(durations), 2) if durations else None,
            'max_response_time': max(durations) if durations else None,
            'min_response_time': min(durations) if durations else None,
            'status_codes': dict(status_codes.most_common(5)),
            'top_endpoints': dict(endpoints.most_common(5)),
            'slow_requests': len([d for d in durations if d > 1000])  # > 1 second
        }

    def _generate_recommendations(self, logs: List[Dict], issue_description: str) -> List[str]:
        """Generate recommendations based on log analysis"""
        recommendations = []

        # Analyze error patterns
        errors = [log for log in logs if log.get('level') == 'ERROR']
        if errors:
            recommendations.append(f"Found {len(errors)} errors in the last 24 hours. Check error details for patterns.")

        # Check for workflow issues
        workflow_errors = [log for log in logs if log.get('event_type') == 'workflow_error']
        if workflow_errors:
            recommendations.append(f"Workflow failures detected ({len(workflow_errors)}). Review workflow configuration and agent execution.")

        # Check for slow requests
        slow_requests = [log for log in logs if log.get('event_type') == 'request_complete' and log.get('duration_ms', 0) > 5000]
        if slow_requests:
            recommendations.append(f"Slow API responses detected ({len(slow_requests)} requests > 5 seconds). Check database queries and external API calls.")

        # Check for incomplete workflows
        workflow_starts = len([log for log in logs if log.get('event_type') == 'workflow_start'])
        workflow_completes = len([log for log in logs if log.get('event_type') == 'workflow_complete'])
        if workflow_starts > workflow_completes:
            incomplete = workflow_starts - workflow_completes
            recommendations.append(f"Found {incomplete} incomplete workflow(s). Check for hangs or timeouts in workflow execution.")

        # Issue-specific recommendations
        issue_lower = issue_description.lower()
        if 'slow' in issue_lower or 'performance' in issue_lower:
            recommendations.append("Performance issue detected. Review database query performance and external API response times.")
        elif 'error' in issue_lower or 'fail' in issue_lower:
            recommendations.append("Error patterns identified. Check recent error logs for root cause analysis.")
        elif 'workflow' in issue_lower:
            recommendations.append("Workflow issue reported. Review workflow execution logs and step failures.")

        if not recommendations:
            recommendations.append("No specific patterns detected. Review recent logs manually for additional context.")

        return recommendations

    def _identify_critical_issues(self, logs: List[Dict]) -> List[Dict]:
        """Identify critical issues requiring immediate attention"""
        critical_issues = []

        # Check for recent errors
        recent_errors = [log for log in logs if log.get('level') == 'ERROR']
        if len(recent_errors) > 10:
            critical_issues.append({
                'type': 'high_error_rate',
                'severity': 'critical',
                'description': f'High error rate: {len(recent_errors)} errors in recent logs',
                'logs': recent_errors[:5]
            })

        # Check for workflow failures
        workflow_failures = [log for log in logs if log.get('event_type') == 'workflow_error']
        if workflow_failures:
            critical_issues.append({
                'type': 'workflow_failures',
                'severity': 'high',
                'description': f'Workflow failures detected: {len(workflow_failures)} failed workflows',
                'logs': workflow_failures[:3]
            })

        # Check for slow performance
        slow_requests = [log for log in logs if log.get('duration_ms', 0) > 10000]  # > 10 seconds
        if slow_requests:
            critical_issues.append({
                'type': 'performance_issues',
                'severity': 'medium',
                'description': f'Severe performance issues: {len(slow_requests)} very slow requests (>10s)',
                'logs': slow_requests[:3]
            })

        return critical_issues

    async def _analyze_logs(self, logs: List[Dict], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive log analysis"""
        if not logs:
            return {}

        return {
            'summary': self._summarize_logs(logs),
            'errors': self._analyze_errors(logs),
            'workflows': self._analyze_workflows(logs),
            'performance': self._analyze_performance(logs),
            'time_range': {
                'from': logs[-1].get('timestamp') if logs else None,
                'to': logs[0].get('timestamp') if logs else None
            }
        }


# Global service instance
log_analysis_service = None

def get_log_analysis_service(db: AsyncIOMotorDatabase) -> LogAnalysisService:
    """Get or create log analysis service instance"""
    global log_analysis_service
    if log_analysis_service is None:
        log_analysis_service = LogAnalysisService(db)
    return log_analysis_service
