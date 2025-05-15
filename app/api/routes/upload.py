import uuid
from typing import  Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.imagejobs import ImageJobs, ImageStatus, JobType
from app.repositories.imagejobs_repository import ImageJobsRepository
from app.schemas.imagejobs import ImageList, ImageResponse
from app.services.storage_service import StorageService
from app.middleware.authentication import supabaseauth

router = APIRouter(
     dependencies=[Depends(supabaseauth.get_current_user)]
)
storage_service = StorageService()

@router.post("/images/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    label: str = Form(...),
    image_type: str = Form(...),
    note: Optional[str] = Form(""),
    priority: str = Form(...),
    user_id: str = Form(...),
    job_type: JobType = Form(...),  # <-- Add this if using new model
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image and store metadata in database
    """
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG, PNG, GIF, and WebP are supported."
        )
    
    try:
        user_uuid = uuid.UUID(user_id)
        
        # Upload file to storage with private access
        storage_path, _ = await storage_service.upload_file(file, user_uuid)
        
        # Create image record in database
        repository = ImageJobsRepository(db)
        image_data = {
            "label": label,
            "image_type": image_type,
            "note": note,
            "priority": priority,
            "user_id": user_uuid,
            "storage_path": storage_path,
            "status": ImageStatus.UPLOADED,
            "job_type": job_type,
            "image_url": "",  # Not stored, will be set in response
            "final_image_url": None
        }
        
        image = await repository.create(image_data)
        # Generate signed URL for response
        signed_url = await storage_service.get_signed_url(storage_path)
        image.image_url = signed_url
        return image
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/images/", response_model=ImageList)
async def get_images(
    user_id: uuid.UUID,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all images for a user with pagination and optional status filter
    """
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    skip = (page - 1) * page_size
    
    repository = ImageJobsRepository(db)
    
    # Filter by status if provided
    filter_params = {"user_id": user_id}
    if status:
        try:
            image_status = ImageStatus(status)
            filter_params["status"] = image_status
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value. Valid values are: {', '.join([s.value for s in ImageStatus])}"
            )
    
    images = await repository.get_by_filters(skip, page_size, **filter_params)
    total = await repository.count_by_filters(**filter_params)
    
    # Refresh signed URLs for all images
    for image in images:
        new_signed_url = await storage_service.get_signed_url(image.storage_path)
        if new_signed_url:
            image.image_url = new_signed_url
    
    return {
        "items": images,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific image by ID
    """
    repository = ImageJobsRepository(db)
    image = await repository.get_by_id(image_id)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Refresh the signed URL
    new_signed_url = await storage_service.get_signed_url(image.storage_path)
    if new_signed_url:
        image.image_url = new_signed_url
        # Note: We're not saving this URL to the database since it's temporary
    
    return image

@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: uuid.UUID,
    permanent: bool = False,  # Set to true for permanent deletion
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an image by ID (soft delete by default)
    """
    repository = ImageJobsRepository(db)
    image = await repository.get_by_id(image_id)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    if permanent:
        # Permanent deletion - remove from storage and database
        storage_deleted = await storage_service.delete_file(image.storage_path)
        db_deleted = await repository.delete(image_id)
        
        if not db_deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete image from database"
            )
    else:
        # Soft deletion - just update status
        await repository.update(image_id, {"status": ImageStatus.DELETED})
    
    return None