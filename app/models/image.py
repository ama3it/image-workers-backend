import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Added user_id field
    label = Column(String, nullable=False)
    image_type = Column(String, nullable=False) 
    note = Column(Text, nullable=True)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Image {self.id}: {self.label}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),  # Include user_id in dict
            "label": self.label,
            "image_type": self.image_type,
            "note": self.note,
            "storage_path": self.storage_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
