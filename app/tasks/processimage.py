import os
from app.celery import celeryapp
from app.models.imageJob import ImageStatus
from app.services.image_processor.processors import process_greyscale, process_thumbnail, process_resize
from app.services.storage_service import StorageService
from app.database import SessionLocal
from uuid import UUID

# Import our new synchronous repository
from app.repositories.sync_image_job_repository import SyncImageJobRepository

DEFAULT_THUMBNAIL_SIZE = (128, 128)
DEFAULT_RESIZE_WIDTH = 800
DEFAULT_RESIZE_HEIGHT = 600

@celeryapp.task(bind=True, name="process_image", max_retries=3)
def process_image(self, image_id, job_id, storage_path, job_type):
    try:
        job_id_uuid = UUID(job_id)
        
        db = SessionLocal()
        try:
            job_repo = SyncImageJobRepository(db)
            job_repo.update_job_status(job_id_uuid, ImageStatus.PROCESSING)
        finally:
            db.close()
        
        storage_service = StorageService()
        image_data = storage_service.download_file_sync(storage_path)

        if job_type == "grayscale":
            processed_path, output_data = process_greyscale(storage_path, image_data)
        elif job_type == "thumbnail":
            processed_path, output_data = process_thumbnail(
                storage_path, image_data, DEFAULT_THUMBNAIL_SIZE
            )
        elif job_type == "resize":
            processed_path, output_data = process_resize(
                storage_path, image_data, DEFAULT_RESIZE_WIDTH, DEFAULT_RESIZE_HEIGHT
            )
        else:
            raise ValueError(f"Unsupported job_type: {job_type}")

        final_storage_path = f"processed/{os.path.basename(processed_path)}"
        storage_service.upload_bytes_sync(output_data, final_storage_path)
        
        # Update the job metadata with completion info using synchronous repository
        db = SessionLocal()
        try:
            job_repo = SyncImageJobRepository(db)
            job_repo.update_job_metadata(job_id_uuid, {
                "status": ImageStatus.COMPLETED,
                "storage_path": final_storage_path 
            })
        finally:
            db.close()

        return {"status": "success", "image_id": image_id, "job_id": job_id}

    except Exception as exc:
        # Handle failure case using synchronous repository
        try:
            db = SessionLocal()
            try:
                job_repo = SyncImageJobRepository(db)
                job_repo.update_job_status(job_id_uuid, ImageStatus.FAILED)
            finally:
                db.close()
        except Exception as inner_exc:
            print(f"[ERROR] Failed to update job status: {inner_exc}")

        print(f"[ERROR] Processing failed for image {image_id}, job {job_id}: {exc}")
        self.retry(exc=exc, countdown=120)
