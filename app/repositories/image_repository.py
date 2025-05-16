from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from uuid import UUID
from app.models.image import Image


class ImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_image(self, image: Image) -> Image:
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def get_image_by_id(self, image_id: UUID) -> Image | None:
        result = await self.session.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    async def list_images(self, limit: int = 100) -> list[Image]:
        result = await self.session.execute(select(Image).limit(limit))
        return result.scalars().all()

    async def list_images_by_user(self, user_id: UUID, limit: int = 100) -> list[Image]:
        result = await self.session.execute(
            select(Image).where(Image.user_id == user_id).limit(limit)
        )
        return result.scalars().all()

    async def delete_image(self, image_id: UUID) -> None:
        await self.session.execute(delete(Image).where(Image.id == image_id))
        await self.session.commit()

    async def update_image_note(self, image_id: UUID, note: str) -> None:
        await self.session.execute(
            update(Image)
            .where(Image.id == image_id)
            .values(note=note)
        )
        await self.session.commit()
