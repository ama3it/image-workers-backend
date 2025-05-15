# app/repositories/image_repository.py
import uuid
from typing import Dict, List, Optional, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.imagejobs import ImageJobs

class ImageJobsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image_data: dict) -> ImageJobs:
        """Create a new image record"""
        # Generate UUID if not provided
        if 'id' not in image_data:
            image_data['id'] = uuid.uuid4()

        image = ImageJobs(**image_data)
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def get_by_id(self, image_id: uuid.UUID) -> Optional[ImageJobs]:
        """Get an image by ID"""
        query = select(ImageJobs).where(ImageJobs.id == image_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[ImageJobs]:
        """Get images by user ID with pagination"""
        query = select(ImageJobs).where(ImageJobs.user_id == user_id).order_by(ImageJobs.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_filters(self, skip: int = 0, limit: int = 100, **filters) -> List[ImageJobs]:
        """Get images by various filters with pagination"""
        query = select(ImageJobs)

        # Apply filters
        for field, value in filters.items():
            if hasattr(ImageJobs, field):
                query = query.where(getattr(ImageJobs, field) == value)

        query = query.order_by(ImageJobs.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Count total images for a user"""
        query = select(func.count()).select_from(ImageJobs).where(ImageJobs.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def count_by_filters(self, **filters) -> int:
        """Count images by various filters"""
        query = select(func.count()).select_from(ImageJobs)

        # Apply filters
        for field, value in filters.items():
            if hasattr(ImageJobs, field):
                query = query.where(getattr(ImageJobs, field) == value)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def delete(self, image_id: uuid.UUID) -> bool:
        """Delete an image by ID"""
        query = delete(ImageJobs).where(ImageJobs.id == image_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_final_image_url(self, image_id: uuid.UUID, final_image_url: str) -> Optional[ImageJobs]:
        """Update the final_image_url of an image job"""
        query = (
            update(ImageJobs)
            .where(ImageJobs.id == image_id)
            .values(final_image_url=final_image_url)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_by_id(image_id)