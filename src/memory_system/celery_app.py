"""Celery application factory."""

from celery import Celery
from celery.schedules import crontab

from memory_system.config import settings

celery = Celery(
    "memory_system",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery.conf.beat_schedule = {
    "decay-update": {
        "task": "memory_system.tasks.decay.batch_update_decay",
        "schedule": crontab(minute="*/30"),
    },
    "consolidation-cycle": {
        "task": "memory_system.tasks.consolidation.run_consolidation",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}

celery.autodiscover_tasks(["memory_system.tasks"])
