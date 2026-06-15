import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from auth import get_current_admin

EXES_DIR = os.getenv(
    "EXES_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "public", "exes"),
)
os.makedirs(EXES_DIR, exist_ok=True)

ALLOWED_EXTS = {".zip", ".exe", ".7z", ".rar"}
MAX_SIZE = 300 * 1024 * 1024  # 300 MB

router = APIRouter(
    prefix="/api/admin/exes",
    tags=["程序下载"],
    dependencies=[Depends(get_current_admin)],
)


class ExeFileRead(BaseModel):
    filename: str
    url: str
    size: int


@router.get("", response_model=list[ExeFileRead])
async def list_exes():
    files = []
    if os.path.isdir(EXES_DIR):
        for name in sorted(os.listdir(EXES_DIR)):
            path = os.path.join(EXES_DIR, name)
            if os.path.isfile(path):
                files.append(ExeFileRead(
                    filename=name,
                    url=f"/exes/{name}",
                    size=os.path.getsize(path),
                ))
    return files


@router.post("", response_model=ExeFileRead)
async def upload_exe(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="只支持 .zip / .exe / .7z / .rar 格式")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 300 MB")

    safe_name = os.path.basename(file.filename or f"file{ext}")
    dest = os.path.join(EXES_DIR, safe_name)
    if os.path.exists(dest):
        stem = os.path.splitext(safe_name)[0]
        safe_name = f"{stem}_{uuid.uuid4().hex[:6]}{ext}"
        dest = os.path.join(EXES_DIR, safe_name)

    with open(dest, "wb") as f:
        f.write(data)

    return ExeFileRead(filename=safe_name, url=f"/exes/{safe_name}", size=len(data))


@router.delete("/{filename}")
async def delete_exe(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="非法文件名")

    path = os.path.join(EXES_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="文件不存在")

    os.remove(path)
    return {"message": "已删除"}
