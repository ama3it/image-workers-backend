from typing import  Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.image import Image
from app.models.imageJob import ImageJob, JobType, ImageStatus
from app.repositories.image_repository import ImageRepository
from app.repositories.image_job_repository import ImageJobRepository
from app.repositories.wallet_repository import WalletRepository
from app.schemas.imagejobs import ImageResponse
from app.services.storage_service import StorageService
from app.middleware.authentication import supabaseauth
from app.services.wallet_service import WalletService
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
    user: dict = Depends(supabaseauth.get_current_user) 
):
    """
    Upload an image, verify payment, store metadata, create a processing job, and enqueue a task.
    Process flow:
    1. Validate file type and user
    2. Upload file to storage
    3. Create image and job record with PENDING_PAYMENT status
    4. Check wallet balance and process payment
    5. If payment succeeds, queue the job for processing
    6. If payment fails, mark job as PAYMENT_FAILED and return error
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
            
        # First upload the image to storage   
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
        
         # Create a job for the uploaded image with PENDING_PAYMENT status
        job_repo = ImageJobRepository(db)
        job = ImageJob(
            image_id=image.id,
            job_type=job_type,
            status=ImageStatus.PENDING_PAYMENT,
            priority=priority,
        )
        job = await job_repo.create_job(job)
        
        # check wallet balance and deduct fee with job ID for reference
        wallet_repo = WalletRepository(db)
        wallet_service = WalletService(wallet_repo)
        has_sufficient_funds, price = await wallet_service.check_and_deduct_balance(
            user_id=user_id, 
            job_type=job_type, 
            priority=priority,
            job_id=str(job.id)  
        )
        
        if not has_sufficient_funds:
            # Update job status to failed due to payment
            await job_repo.update_job_status(job.id, ImageStatus.PAYMENT_FAILED)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient funds. This operation requires {price} credits."
            )
        
        # If payment successful, update status and queue the job
        await job_repo.update_job_status(job.id, ImageStatus.QUEUED)
        
        # Queue task for processing
        process_image.delay(
            image_id=str(image.id),
            job_id=str(job.id),
            storage_path=storage_path,
            job_type=job_type
        )

        await job_repo.update_job_status(job.id, ImageStatus.QUEUED)
    
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