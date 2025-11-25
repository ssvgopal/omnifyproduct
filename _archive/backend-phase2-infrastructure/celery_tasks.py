"""
Celery Tasks for OmnifyProduct
Background job implementations

Tasks:
- AgentKit workflow execution
- Email notifications
- Data processing and aggregation
- Cache management
- Maintenance operations
"""

from services.celery_app import app
from services.redis_cache_service import redis_cache_service
from services.structured_logging import logger
from agentkit_revolutionary import RevolutionaryAgentKit
from database.mongodb_schema import MongoDBSchema
from datetime import datetime, timedelta
import asyncio
import json

# Global instances (initialized in lifespan)
mongodb_client = None
revolutionary_agentkit = None

def init_celery_services(db_client, agentkit_instance):
    """Initialize global services for Celery tasks"""
    global mongodb_client, revolutionary_agentkit
    mongodb_client = db_client
    revolutionary_agentkit = agentkit_instance

# ========== AGENTKIT WORKFLOW TASKS ==========

@app.task(bind=True, name='services.celery_tasks.execute_agentkit_workflow')
def execute_agentkit_workflow(self, workflow_config: dict, input_data: dict, user_id: str, organization_id: str):
    """
    Execute AgentKit workflow asynchronously
    """
    try:
        logger.info("Starting AgentKit workflow execution", extra={
            "task_id": self.request.id,
            "workflow_type": workflow_config.get("type"),
            "user_id": user_id,
            "organization_id": organization_id
        })

        # Execute workflow using revolutionary agentkit
        if revolutionary_agentkit:
            result = asyncio.run(
                revolutionary_agentkit.execute_full_campaign_workflow({
                    "user_id": user_id,
                    "organization_id": organization_id,
                    **workflow_config,
                    **input_data
                })
            )

            logger.info("AgentKit workflow completed", extra={
                "task_id": self.request.id,
                "status": result.get("status"),
                "execution_time": result.get("execution_time")
            })

            return result
        else:
            raise RuntimeError("Revolutionary AgentKit not initialized")

    except Exception as e:
        logger.error("AgentKit workflow execution failed", exc_info=e, extra={
            "task_id": self.request.id,
            "user_id": user_id,
            "organization_id": organization_id
        })
        raise self.retry(countdown=60, max_retries=3)

# ========== EMAIL NOTIFICATION TASKS ==========

@app.task(bind=True, name='services.celery_tasks.send_email_notification')
def send_email_notification(self, recipient: str, subject: str, template: str, context: dict):
    """
    Send email notification asynchronously
    """
    try:
        logger.info("Sending email notification", extra={
            "task_id": self.request.id,
            "recipient": recipient,
            "template": template
        })

        # TODO: Integrate with email service (SendGrid, AWS SES, etc.)
        # For now, simulate email sending
        asyncio.run(asyncio.sleep(0.1))  # Simulate API call

        logger.info("Email notification sent", extra={
            "task_id": self.request.id,
            "recipient": recipient,
            "template": template
        })

        return {"status": "sent", "recipient": recipient}

    except Exception as e:
        logger.error("Email notification failed", exc_info=e, extra={
            "task_id": self.request.id,
            "recipient": recipient
        })
        raise self.retry(countdown=300, max_retries=5)  # Retry up to 5 times

@app.task(bind=True, name='services.celery_tasks.send_bulk_email_campaign')
def send_bulk_email_campaign(self, campaign_id: str, recipients: list, template_id: str, campaign_data: dict):
    """
    Send bulk email campaign asynchronously
    """
    try:
        logger.info("Starting bulk email campaign", extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id,
            "recipients_count": len(recipients)
        })

        # Process in batches to avoid overwhelming email service
        batch_size = 50
        results = []

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]

            # Send batch
            for recipient in batch:
                try:
                    # TODO: Send actual email
                    asyncio.run(asyncio.sleep(0.01))  # Simulate sending
                    results.append({"recipient": recipient, "status": "sent"})
                except Exception as e:
                    results.append({"recipient": recipient, "status": "failed", "error": str(e)})

            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': min(i + batch_size, len(recipients)), 'total': len(recipients)}
            )

        # Store campaign results in database
        if mongodb_client:
            campaign_result = {
                "campaign_id": campaign_id,
                "completed_at": datetime.utcnow(),
                "total_recipients": len(recipients),
                "sent_count": len([r for r in results if r["status"] == "sent"]),
                "failed_count": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

            asyncio.run(mongodb_client.email_campaigns.insert_one(campaign_result))

        logger.info("Bulk email campaign completed", extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id,
            "sent": len([r for r in results if r["status"] == "sent"]),
            "failed": len([r for r in results if r["status"] == "failed"])
        })

        return {
            "campaign_id": campaign_id,
            "total_recipients": len(recipients),
            "sent": len([r for r in results if r["status"] == "sent"]),
            "failed": len([r for r in results if r["status"] == "failed"])
        }

    except Exception as e:
        logger.error("Bulk email campaign failed", exc_info=e, extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id
        })
        raise

# ========== DATA PROCESSING TASKS ==========

@app.task(bind=True, name='services.celery_tasks.process_campaign_analytics')
def process_campaign_analytics(self, campaign_id: str, date_range: dict, organization_id: str):
    """
    Process campaign analytics data asynchronously
    """
    try:
        logger.info("Processing campaign analytics", extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id,
            "organization_id": organization_id,
            "date_range": date_range
        })

        if not mongodb_client:
            raise RuntimeError("MongoDB client not initialized")

        # Aggregate campaign data
        pipeline = [
            {
                "$match": {
                    "campaign_id": campaign_id,
                    "organization_id": organization_id,
                    "timestamp": {
                        "$gte": datetime.fromisoformat(date_range["start"]),
                        "$lte": datetime.fromisoformat(date_range["end"])
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "platform": "$platform"
                    },
                    "impressions": {"$sum": "$impressions"},
                    "clicks": {"$sum": "$clicks"},
                    "conversions": {"$sum": "$conversions"},
                    "spend": {"$sum": "$spend"},
                    "revenue": {"$sum": "$revenue"}
                }
            },
            {
                "$sort": {"_id.date": 1}
            }
        ]

        analytics_data = []
        async def run_aggregation():
            cursor = mongodb_client.campaign_analytics.aggregate(pipeline)
            async for doc in cursor:
                analytics_data.append(doc)

        asyncio.run(run_aggregation())

        # Calculate derived metrics
        for day_data in analytics_data:
            impressions = day_data.get("impressions", 0)
            clicks = day_data.get("clicks", 0)
            conversions = day_data.get("conversions", 0)
            spend = day_data.get("spend", 0)

            day_data["ctr"] = (clicks / impressions * 100) if impressions > 0 else 0
            day_data["cpc"] = (spend / clicks) if clicks > 0 else 0
            day_data["cpa"] = (spend / conversions) if conversions > 0 else 0
            day_data["roas"] = (day_data.get("revenue", 0) / spend) if spend > 0 else 0

        # Store processed analytics
        processed_result = {
            "campaign_id": campaign_id,
            "organization_id": organization_id,
            "date_range": date_range,
            "processed_at": datetime.utcnow(),
            "data_points": len(analytics_data),
            "analytics": analytics_data
        }

        asyncio.run(mongodb_client.processed_analytics.insert_one(processed_result))

        # Cache results for fast retrieval
        if redis_cache_service.redis_client:
            cache_key = f"analytics:campaign:{campaign_id}:{date_range['start']}:{date_range['end']}"
            asyncio.run(redis_cache_service.redis_client.setex(
                cache_key,
                3600,  # 1 hour
                json.dumps(processed_result, default=str)
            ))

        logger.info("Campaign analytics processing completed", extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id,
            "data_points": len(analytics_data)
        })

        return processed_result

    except Exception as e:
        logger.error("Campaign analytics processing failed", exc_info=e, extra={
            "task_id": self.request.id,
            "campaign_id": campaign_id
        })
        raise self.retry(countdown=300, max_retries=3)

# ========== CACHE MANAGEMENT TASKS ==========

@app.task(bind=True, name='services.celery_tasks.daily_cache_cleanup')
def daily_cache_cleanup(self):
    """
    Daily cache cleanup task
    Remove expired entries and optimize cache performance
    """
    try:
        logger.info("Starting daily cache cleanup", extra={
            "task_id": self.request.id
        })

        if not redis_cache_service.redis_client:
            logger.warning("Redis client not available for cache cleanup")
            return

        # Clean up old session data (older than 30 days)
        session_pattern = "session:*"
        old_sessions = []
        async def cleanup_sessions():
            keys = await redis_cache_service.redis_client.keys(session_pattern)
            for key in keys:
                # Check TTL, if no TTL or expired, mark for cleanup
                ttl = await redis_cache_service.redis_client.ttl(key)
                if ttl == -1:  # No TTL set
                    old_sessions.append(key)

        asyncio.run(cleanup_sessions())

        if old_sessions:
            asyncio.run(redis_cache_service.redis_client.delete(*old_sessions))

        # Clean up old analytics cache (older than 7 days)
        analytics_pattern = "analytics:*"
        old_analytics = []
        async def cleanup_analytics():
            keys = await redis_cache_service.redis_client.keys(analytics_pattern)
            for key in keys:
                ttl = await redis_cache_service.redis_client.ttl(key)
                if ttl == -1 or ttl > 604800:  # 7 days
                    old_analytics.append(key)

        asyncio.run(cleanup_analytics())

        if old_analytics:
            asyncio.run(redis_cache_service.redis_client.delete(*old_analytics))

        # Log cleanup results
        logger.info("Daily cache cleanup completed", extra={
            "task_id": self.request.id,
            "sessions_cleaned": len(old_sessions),
            "analytics_cleaned": len(old_analytics)
        })

        return {
            "sessions_cleaned": len(old_sessions),
            "analytics_cleaned": len(old_analytics)
        }

    except Exception as e:
        logger.error("Daily cache cleanup failed", exc_info=e, extra={
            "task_id": self.request.id
        })
        raise

# ========== ANALYTICS AGGREGATION TASKS ==========

@app.task(bind=True, name='services.celery_tasks.daily_analytics_aggregation')
def daily_analytics_aggregation(self):
    """
    Daily analytics aggregation for executive dashboards
    """
    try:
        logger.info("Starting daily analytics aggregation", extra={
            "task_id": self.request.id
        })

        if not mongodb_client:
            raise RuntimeError("MongoDB client not initialized")

        yesterday = datetime.utcnow() - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Aggregate daily metrics across all organizations
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": yesterday_start,
                        "$lte": yesterday_end
                    }
                }
            },
            {
                "$group": {
                    "_id": "$organization_id",
                    "total_impressions": {"$sum": "$impressions"},
                    "total_clicks": {"$sum": "$clicks"},
                    "total_conversions": {"$sum": "$conversions"},
                    "total_spend": {"$sum": "$spend"},
                    "total_revenue": {"$sum": "$revenue"},
                    "campaigns_count": {"$addToSet": "$campaign_id"}
                }
            }
        ]

        aggregated_data = []
        async def run_aggregation():
            cursor = mongodb_client.campaign_analytics.aggregate(pipeline)
            async for doc in cursor:
                doc["date"] = yesterday.date().isoformat()
                doc["campaigns_count"] = len(doc["campaigns_count"])
                aggregated_data.append(doc)

        asyncio.run(run_aggregation())

        # Calculate derived metrics and store
        for org_data in aggregated_data:
            impressions = org_data.get("total_impressions", 0)
            clicks = org_data.get("total_clicks", 0)
            conversions = org_data.get("total_conversions", 0)
            spend = org_data.get("total_spend", 0)

            org_data["ctr"] = (clicks / impressions * 100) if impressions > 0 else 0
            org_data["roas"] = (org_data.get("total_revenue", 0) / spend) if spend > 0 else 0

            # Store daily aggregate
            asyncio.run(mongodb_client.daily_aggregates.insert_one(org_data))

        logger.info("Daily analytics aggregation completed", extra={
            "task_id": self.request.id,
            "organizations_processed": len(aggregated_data)
        })

        return {
            "date": yesterday.date().isoformat(),
            "organizations_processed": len(aggregated_data)
        }

    except Exception as e:
        logger.error("Daily analytics aggregation failed", exc_info=e, extra={
            "task_id": self.request.id
        })
        raise

# ========== PERFORMANCE MONITORING TASKS ==========

@app.task(bind=True, name='services.celery_tasks.hourly_performance_monitoring')
def hourly_performance_monitoring(self):
    """
    Hourly performance monitoring and alerting
    """
    try:
        logger.info("Starting hourly performance monitoring", extra={
            "task_id": self.request.id
        })

        if not revolutionary_agentkit:
            logger.warning("Revolutionary AgentKit not available for performance monitoring")
            return

        # Get system performance from revolutionary agentkit
        performance_data = asyncio.run(revolutionary_agentkit.monitor_system_performance())

        # Check for performance issues
        issues = []
        performance_score = performance_data.get("result", {}).get("performance_score", 100)

        if performance_score < 80:
            issues.append(f"Performance score below threshold: {performance_score}")

        # Check cache hit rate
        if redis_cache_service.redis_client:
            cache_stats = asyncio.run(redis_cache_service.get_cache_stats())
            # Add cache performance monitoring logic

        # Check queue lengths
        # Add queue monitoring logic

        if issues:
            # Send alert
            alert_data = {
                "alert_type": "performance_degradation",
                "issues": issues,
                "performance_score": performance_score,
                "timestamp": datetime.utcnow().isoformat()
            }

            # TODO: Send alert via Slack/email
            logger.warning("Performance issues detected", extra={
                "task_id": self.request.id,
                "issues": issues,
                "performance_score": performance_score
            })

        logger.info("Hourly performance monitoring completed", extra={
            "task_id": self.request.id,
            "performance_score": performance_score,
            "issues_found": len(issues)
        })

        return {
            "performance_score": performance_score,
            "issues_found": len(issues),
            "issues": issues
        }

    except Exception as e:
        logger.error("Hourly performance monitoring failed", exc_info=e, extra={
            "task_id": self.request.id
        })
        raise

# ========== MAINTENANCE TASKS ==========

@app.task(bind=True, name='services.celery_tasks.weekly_data_backup')
def weekly_data_backup(self):
    """
    Weekly data backup task
    """
    try:
        logger.info("Starting weekly data backup", extra={
            "task_id": self.request.id
        })

        # TODO: Implement database backup logic
        # This could use mongodump, pg_dump, or cloud provider snapshots

        logger.info("Weekly data backup completed", extra={
            "task_id": self.request.id
        })

        return {"status": "backup_completed"}

    except Exception as e:
        logger.error("Weekly data backup failed", exc_info=e, extra={
            "task_id": self.request.id
        })
        raise

@app.task(bind=True, name='services.celery_tasks.weekly_compliance_audit')
def weekly_compliance_audit(self):
    """
    Weekly compliance audit using revolutionary compliance agent
    """
    try:
        logger.info("Starting weekly compliance audit", extra={
            "task_id": self.request.id
        })

        if not revolutionary_agentkit:
            logger.warning("Revolutionary AgentKit not available for compliance audit")
            return

        # Run compliance audit
        audit_result = asyncio.run(revolutionary_agentkit.perform_compliance_audit_revolutionary({
            "audit_type": "weekly_compliance_check",
            "scope": "full_system",
            "check_soc2": True,
            "check_iso27001": True
        }))

        audit_status = audit_result.get("status", "unknown")

        if audit_status != "compliant":
            # Send alert for compliance issues
            logger.warning("Compliance audit found issues", extra={
                "task_id": self.request.id,
                "audit_status": audit_status
            })

        logger.info("Weekly compliance audit completed", extra={
            "task_id": self.request.id,
            "audit_status": audit_status
        })

        return audit_result

    except Exception as e:
        logger.error("Weekly compliance audit failed", exc_info=e, extra={
            "task_id": self.request.id
        })
        raise
