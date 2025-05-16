import os
import uuid
from typing import BinaryIO, Optional, Tuple
import httpx
import requests
from fastapi import UploadFile, HTTPException, status
from app.config import settings

class StorageService:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
    
    async def upload_file(self, file: UploadFile, user_id: uuid.UUID) -> Tuple[str, str]:
        """
        Upload a file to Supabase Storage with private access.
        Returns (storage_path, public_url)
        - storage_path: The path in the bucket (store this in DB for later retrieval/deletion)
        - public_url: The signed URL for temporary access (do NOT store in DB, generate when needed)
        """
        try:
            # Generate a unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create folder structure with user ID for additional isolation
            folder_path = f"user_{str(user_id)}"
            file_path = f"{folder_path}/{unique_filename}"
            
            # Read file content
            content = await file.read()
            
            # Upload to Supabase Storage
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                    headers={
                        **self.headers,
                        "Content-Type": file.content_type or "application/octet-stream"
                    },
                    content=content
                )
                response.raise_for_status()
            
            # Store file_path (storage_path) in DB for future reference
            # Do NOT store signed_url in DB, always generate on demand
            
            # Get a signed URL with temporary access (for immediate use)
            signed_url = await self.get_signed_url(file_path)
            if not signed_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate signed URL"
                )
            
            return file_path, signed_url
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a signed URL for temporary access to a private file.
        Always generate this on demand, do not store in DB.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/storage/v1/object/sign/{self.bucket_name}/{file_path}",
                    headers=self.headers,
                    json={"expiresIn": expires_in}
                )
                response.raise_for_status()
                data = response.json()
                # Supabase returns {"signedURL": "..."}
                return data.get("signedURL")
        except Exception as e:
            print(f"Error getting signed URL: {str(e)}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage.
        Use the storage_path stored in DB to delete.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                    headers=self.headers
                )
                response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def download_file_sync(self, file_path: str) -> bytes:
        """
        Synchronously download a file from Supabase Storage.
        Returns the file content as bytes.
        """
        try:
            response = requests.get(
                f"{self.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return b""
    
    def upload_bytes_sync(self, file_bytes: bytes, file_path: str, content_type: str = "application/octet-stream") -> bool:
        """
        Synchronously upload bytes to Supabase Storage.
        Returns True if upload is successful, False otherwise.
        """
        try:
            response = requests.post(
                f"{self.url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers={
                    **self.headers,
                    "Content-Type": content_type
                },
                data=file_bytes
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error uploading bytes: {str(e)}")
            return False