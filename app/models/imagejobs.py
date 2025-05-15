import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class ImageStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

class JobType(str, enum.Enum):
    RESIZE = "resize"
    THUMBNAIL = "thumbnail"
    GRAYSCALE = "grayscale"

class ImageJobs(Base):
    __tablename__ = "imagejobs" 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String, nullable=False)
    image_type = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    priority = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    image_url = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)  # Store the path for access control
    status = Column(Enum(ImageStatus), default=ImageStatus.UPLOADED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now(), nullable=False)
    job_type = Column(Enum(JobType), nullable=False)  # New field for job type
    final_image_url = Column(String, nullable=True)   # New field for final image location on Supabase storage

    def __repr__(self):
        return f"<ImageJobs {self.id}: {self.label} ({self.status})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "label": self.label,
            "image_type": self.image_type,
            "note": self.note,
            "priority": self.priority,
            "user_id": str(self.user_id),
            "image_url": self.image_url,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "job_type": self.job_type,
            "final_image_url": self.final_image_url,
        }