from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from google.api_core import exceptions
from google.cloud import storage  # type: ignore
from pydantic import BaseModel

router = APIRouter()

# Consider moving this to a config/environment variable
BUCKET_NAME = "audition-storage"
ALLOWED_EXTENSIONS = {
    # ".mp3", ".wav", ".m4a", ".aac",
    ".webm",
}
MAX_FILENAME_LENGTH = 200

storage_client = storage.Client.from_service_account_json(
    "secrets/storage_key.json"
)


def validate_filename(filename: str) -> str:
    """Validate and sanitize the filename, returning a storage-safe version."""
    if not filename or len(filename) > MAX_FILENAME_LENGTH:
        raise HTTPException(
            status_code=400, detail="Invalid filename length"
        )

    ext = "." + filename.split(".")[-1] if "." in filename else ""
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Generate a unique filename while preserving the extension
    safe_filename = f"{uuid4()}{ext}"
    return safe_filename


class GenerateUploadUrlRequest(BaseModel):
    interview_session_id: str
    filename: str
    content_type: str


@router.post("/generate-upload-url")
async def generate_upload_url(
    request: GenerateUploadUrlRequest,
) -> dict[str, Any]:
    """
    Generate a signed URL for secure file uploads to Google Cloud Storage.

    Args:
        filename: Original filename with extension
        content_type: MIME type of the file being uploaded

    Returns:
        Dictionary containing the signed URL and the storage filename
    """
    folder_prefix = f"auditions/{request.interview_session_id}/"
    try:
        storage_filename = validate_filename(request.filename)
        blob_name = f"{folder_prefix}{storage_filename}"
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type=request.content_type,
            headers={
                "x-goog-content-length-range": "0,1000000000",  # Max 1GB
            },
        )

        return {
            "url": url,
            "storage_filename": blob_name,
            "expires_in": 900,  # 15 minutes in seconds
        }

    except exceptions.GoogleAPIError as e:
        raise HTTPException(
            status_code=500, detail="Failed to generate upload URL"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to generate upload URL"
        ) from e
