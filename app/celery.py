from celery import Celery
from pydantic_settings import BaseSettings
from typing import List

class CeleryConfig(BaseSettings):
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    accept_content: List[str] = ["json"]
    task_serializer: str = "json"
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    task_time_limit: int = 600  # 10 minutes max task execution time
    worker_prefetch_multiplier: int = 1  # Process tasks one at a time


def create_celery_app() -> Celery:
    app = Celery("image_processor")
    app.config_from_object(CeleryConfig(), namespace="CELERY")
    return app

celeryapp = create_celery_app()

# Import tasks so Celery can register them
import app.tasks.processimage