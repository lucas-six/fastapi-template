"""Celery Configuration."""

from datetime import timedelta

from celery.schedules import crontab

from app.settings import get_settings

settings = get_settings()

timezone = settings.task_timezone
enable_utc = True
task_time_limit = settings.task_time_limit
result_expires = settings.task_queue_result_expires

beat_schedule = {
    'do_something': {
        'task': 'task.celery_worker.do_something',
        'schedule': crontab(hour='2', minute='30'),
    },
    'heartbeat': {
        'task': 'task.celery_worker.heartbeat',
        'schedule': timedelta(seconds=30),
    },
}
