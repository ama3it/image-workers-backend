from sqlalchemy import update, delete
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.imageJob import ImageJob
from typing import Dict, Any, Optional, List

class SyncImageJobRepository:
    """
    Synchronous version of the ImageJobRepository for use in Celery tasks.
    """
    def __init__(self, session: Session):
        self.session = session

    def create_job(self, job: ImageJob) -> ImageJob:
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get_job_by_id(self, job_id: UUID) -> Optional[ImageJob]:
        return self.session.query(ImageJob).filter(ImageJob.id == job_id).first()

    def list_jobs_for_image(self, image_id: UUID) -> List[ImageJob]:
        return self.session.query(ImageJob).filter(ImageJob.image_id == image_id).all()

    def update_job_status(self, job_id: UUID, status: str) -> None:
        stmt = update(ImageJob).where(ImageJob.id == job_id).values(status=status)
        self.session.execute(stmt)
        self.session.commit()

    def delete_job(self, job_id: UUID) -> None:
        stmt = delete(ImageJob).where(ImageJob.id == job_id)
        self.session.execute(stmt)
        self.session.commit()

    def update_job_metadata(self, job_id: UUID, values: Dict[str, Any]) -> None:
        stmt = update(ImageJob).where(ImageJob.id == job_id).values(**values)
        self.session.execute(stmt)
        self.session.commit()
