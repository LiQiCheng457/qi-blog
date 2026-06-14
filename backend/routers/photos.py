import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Photo, PhotoRead, PhotoUpdate
from auth import get_current_admin

router = APIRouter(prefix="/api/photos", tags=["图片"])

PHOTOS_DIR = os.getenv(
    "PHOTOS_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "public", "photos"),
)
os.makedirs(PHOTOS_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("", response_model=list[PhotoRead])
async def list_photos(
    tag: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Photo)
    if tag:
        stmt = stmt.where(Photo.tag == tag)
    stmt = stmt.order_by(Photo.sort_order.asc(), Photo.created_at.asc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=PhotoRead, dependencies=[Depends(get_current_admin)])
async def upload_photo(
    file: UploadFile = File(...),
    alt: str = Form(default=""),
    tag: str = Form(default=""),
    session: AsyncSession = Depends(get_session),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="只支持 JPG / PNG / WebP / GIF")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 10 MB")

    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(PHOTOS_DIR, filename)
    with open(dest, "wb") as f:
        f.write(data)

    photo = Photo(url=f"/photos/{filename}", alt=alt, tag=tag)
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


@router.patch("/{photo_id}", response_model=PhotoRead, dependencies=[Depends(get_current_admin)])
async def update_photo(
    photo_id: int,
    data: PhotoUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="图片不存在")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(photo, key, value)
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    return photo


@router.delete("/{photo_id}", dependencies=[Depends(get_current_admin)])
async def delete_photo(
    photo_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="图片不存在")

    filename = os.path.basename(photo.url)
    filepath = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    await session.delete(photo)
    await session.commit()
    return {"message": "已删除"}
