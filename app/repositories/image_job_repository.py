from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from uuid import UUID
from app.models.imageJob import ImageJob


class ImageJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job: ImageJob) -> ImageJob:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job_by_id(self, job_id: UUID) -> ImageJob | None:
        result = await self.session.execute(
            select(ImageJob).where(ImageJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_jobs_for_image(self, image_id: UUID) -> list[ImageJob]:
        result = await self.session.execute(
            select(ImageJob).where(ImageJob.image_id == image_id)
        )
        return result.scalars().all()

    async def update_job_status(self, job_id: UUID, status: str) -> None:
        await self.session.execute(
            update(ImageJob).where(ImageJob.id == job_id).values(status=status)
        )
        await self.session.commit()

    async def delete_job(self, job_id: UUID) -> None:
        await self.session.execute(delete(ImageJob).where(ImageJob.id == job_id))
        await self.session.commit()


    async def update_job_metadata(self, job_id: UUID, values: dict):
        await self.session.execute(
            update(ImageJob).where(ImageJob.id == job_id).values(**values)
        )
        await self.session.commit()
        
    