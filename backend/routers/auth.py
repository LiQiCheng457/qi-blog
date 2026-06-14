"""保留 OAuth2 token 端点，现在用统一 User 表认证"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import User, UserRead
from auth import verify_password, create_access_token, get_current_user
from sqlmodel import SQLModel

router = APIRouter(prefix="/api/auth", tags=["认证"])


class Token(SQLModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """OAuth2 兼容接口（支持用户名或邮箱）"""
    result = await session.execute(
        select(User).where(
            or_(User.username == form_data.username, User.email == form_data.username)
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def check_auth(user: User = Depends(get_current_user)):
    return user
