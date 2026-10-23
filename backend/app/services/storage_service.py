import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps
import io
from backend.app.core.config import settings
from backend.app.core.errors import ValidationError
from backend.app.core.logging import logger

# Supported magic bytes signatures
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp"
}

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.STORAGE_DIR).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_and_save_image(self, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Validates magic bytes, file size, image dimensions, and saves image with random UUID.
        Returns: (storage_key, relative_url)
        """
        # 1. Size check
        if len(file_bytes) > settings.ASSESSMENT_MAX_UPLOAD_BYTES:
            raise ValidationError(
                f"Image file exceeds maximum allowed size of {settings.ASSESSMENT_MAX_UPLOAD_BYTES // (1024*1024)} MB."
            )
        if len(file_bytes) < 100:
            raise ValidationError("File is too small or empty to be a valid image.")

        # 2. Magic bytes check
        mime_type = None
        for magic, mime in MAGIC_BYTES.items():
            if file_bytes.startswith(magic):
                # For WebP, check 'WEBP' at offset 8
                if magic == b"RIFF" and file_bytes[8:12] != b"WEBP":
                    continue
                mime_type = mime
                break

        if not mime_type or mime_type not in settings.ALLOWED_IMAGE_MIMETYPES:
            raise ValidationError("Invalid image format. Only JPEG, PNG, and WebP images are accepted.")

        # 3. Decode & dimension checks with PIL
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()
            # Reopen for metadata inspection
            with Image.open(io.BytesIO(file_bytes)) as img:
                width, height = img.size
                if width < 50 or height < 50:
                    raise ValidationError("Image resolution is too low for agricultural diagnosis (min 50x50 px).")
                if width > 4096 or height > 4096:
                    raise ValidationError("Image resolution is too high (max 4096x4096 px). Please resize.")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Image could not be safely decoded: {str(e)}")

        # 4. Generate random UUID key
        ext = "jpg" if mime_type == "image/jpeg" else ("png" if mime_type == "image/png" else "webp")
        storage_key = f"{uuid.uuid4().hex}.{ext}"
        destination = self.upload_dir / storage_key

        with open(destination, "wb") as f:
            f.write(file_bytes)

        logger.info("Crop image stored securely", extra={"extra_data": {"storage_key": storage_key, "size_bytes": len(file_bytes)}})
        relative_url = f"/api/v1/assessments/images/{storage_key}"
        return storage_key, relative_url

    def get_image_path(self, storage_key: str) -> Optional[Path]:
        """
        Returns validated path to image file with strict directory traversal prevention.
        """
        safe_key = Path(storage_key).name  # strip any directory component
        file_path = (self.upload_dir / safe_key).resolve()
        
        # Guard against traversal
        if not str(file_path).startswith(str(self.upload_dir)):
            return None
        if not file_path.exists():
            return None
        return file_path

storage_service = StorageService()
