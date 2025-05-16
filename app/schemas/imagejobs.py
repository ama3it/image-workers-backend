from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, UUID4

# Enum for image status
class ImageStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

# Enum for job type
class JobType(str, Enum):
    RESIZE = "resize"
    THUMBNAIL = "thumbnail"
    GRAYSCALE = "grayscale"

# Request schemas for validation
class ImageCreate(BaseModel):
    label: str
    image_type: str
    note: Optional[str] = None
    priority: str
    user_id: UUID4
    status: ImageStatus = ImageStatus.UPLOADED
    job_type: JobType 

    class Config:
        from_attributes = True

# Update schema
class ImageUpdate(BaseModel):
    label: Optional[str] = None
    note: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[ImageStatus] = None
    job_type: Optional[JobType] = None

    class Config:
        from_attributes = True

# Response schemas for consistent API output
class ImageResponse(BaseModel):
    id: UUID4
    label: str
    image_type: str
    note: Optional[str] = None
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    storage_path: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID4: lambda v: str(v)
        }

# Schema for image listing with pagination
class ImageList(BaseModel):
    items: list[ImageResponse]
    total: int
    page: int