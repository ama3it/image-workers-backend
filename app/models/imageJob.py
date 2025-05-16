from datetime import datetime
import uuid
from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String
from app.database import Base
import enum


class ImageStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(str, enum.Enum):
    RESIZE = "resize"
    THUMBNAIL = "thumbnail"
    GRAYSCALE = "grayscale"

class ImageJob(Base):
    __tablename__ = "image_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(ImageStatus), default=ImageStatus.UPLOADED, nullable=False)
    priority = Column(String, nullable=False)
    storage_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<ImageJob {self.id}: {self.job_type} ({self.status})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "image_id": str(self.image_id),
            "job_type": self.job_type,
            "status": self.status,
            "priority": self.priority,
            "storage_path": self.storage_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
