from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.auth import AdminRequired
from app.config import settings
from app.schemas import AssetRead

router = APIRouter(prefix="/assets", tags=["assets"])

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "model/gltf-binary": ".glb",
    "application/octet-stream": ".glb",
}
CHUNK_SIZE = 1024 * 1024


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def upload_asset(file: UploadFile, _: AdminRequired) -> AssetRead:
    original_suffix = Path(file.filename or "").suffix.lower()
    expected_suffix = ALLOWED_TYPES.get(file.content_type or "")
    if expected_suffix is None or original_suffix != expected_suffix:
        raise HTTPException(status_code=415, detail="仅支持 JPG、PNG、WEBP 图片和 GLB 模型")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{expected_suffix}"
    destination = upload_dir / stored_name
    maximum = settings.max_upload_mb * 1024 * 1024
    size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > maximum:
                    raise HTTPException(
                        status_code=413, detail=f"文件不能超过 {settings.max_upload_mb} MB"
                    )
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return AssetRead(
        filename=stored_name,
        url=f"/uploads/{stored_name}",
        content_type=file.content_type or "application/octet-stream",
        size=size,
    )
