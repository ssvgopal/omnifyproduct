"""
Celery Configuration for OmnifyProduct
Background job processing with RabbitMQ/Redis

Features:
- AgentKit workflow execution
- Email notifications
- Data processing tasks
- Scheduled maintenance jobs
- Error handling and retries
"""

import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Celery app configuration
app = Celery('omnify_product')

# Load configuration from environment
app.conf.update(
    broker_url=os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/'),
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    beat_schedule={
        # Daily maintenance tasks
        'daily-cache-cleanup': {
            'task': 'services.celery_app.daily_cache_cleanup',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
        'daily-analytics-aggregation': {
            'task': 'services.celery_app.daily_analytics_aggregation',
            'schedule': crontab(hour=3, minute=0),  # 3 AM daily
        },
        'hourly-performance-monitoring': {
            'task': 'services.celery_app.hourly_performance_monitoring',
            'schedule': crontab(minute=0),  # Every hour
        },
        # Weekly tasks
        'weekly-data-backup': {
            'task': 'services.celery_app.weekly_data_backup',
            'schedule': crontab(hour=1, minute=0, day_of_week=0),  # Sunday 1 AM
        },
        'weekly-compliance-audit': {
            'task': 'services.celery_app.weekly_compliance_audit',
            'schedule': crontab(hour=4, minute=0, day_of_week=1),  # Monday 4 AM
        },
    }
)

# Import tasks
from services.celery_tasks import *

if __name__ == '__main__':
    app.start()
