from typing import  Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.image import Image
from app.models.imageJob import ImageJob, JobType, ImageStatus
from app.repositories.image_repository import ImageRepository
from app.repositories.image_job_repository import ImageJobRepository
from app.schemas.imagejobs import ImageResponse
from app.services.storage_service import StorageService
from app.middleware.authentication import supabaseauth
from app.tasks.processimage import process_image

router = APIRouter(
     dependencies=[Depends(supabaseauth.get_current_user)]
)
storage_service = StorageService()

@router.post("/process/image/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    label: str = Form(...),
    image_type: str = Form(...),
    note: Optional[str] = Form(""),
    priority: str = Form(...),
    job_type: JobType = Form(...),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(supabaseauth.get_current_user)  # Add this line
):
    """
    Upload an image, store metadata, create a processing job, and enqueue a task
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only JPEG, PNG, and WebP are supported."
        )

    try:
        user_id = user.get("id")
        if not user_id: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        storage_path, _ = await storage_service.upload_file(file, user_id=user_id)
        # Create image record
        image_repo = ImageRepository(db)
        image = Image(
            label=label,
            image_type=image_type,
            note=note,
            storage_path=storage_path,
            user_id=user_id,  
        )
        image = await image_repo.create_image(image)
        
        # Create a job for the uploaded image
        job_repo = ImageJobRepository(db)
        job = ImageJob(
            image_id=image.id,
            job_type=job_type,
            status=ImageStatus.QUEUED,
            priority=priority,
        )
        job = await job_repo.create_job(job)
     
        
        process_image.delay(
            image_id=str(image.id),
            job_id=str(job.id),
            storage_path=storage_path,
            job_type=job_type
        )

        await job_repo.update_job_status(job.id, ImageStatus.QUEUED)
       
        print(f"Job created with ID: {job.id} for image ID: {image.id}")

        return ImageResponse(
            id=image.id,
            user_id=image.user_id,
            label=image.label,
            image_type=image.image_type,
            note=image.note,
            storage_path=image.storage_path,
            created_at=image.created_at,
            updated_at=image.updated_at
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )