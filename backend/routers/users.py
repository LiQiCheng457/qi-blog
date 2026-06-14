from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, or_, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import User, UserRegister, UserLogin, UserRead, UserUpdate
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(data: UserRegister, session: AsyncSession = Depends(get_session)):
    if len(data.username) < 2:
        raise HTTPException(400, "用户名至少 2 个字符")
    if len(data.password) < 6:
        raise HTTPException(400, "密码至少 6 位")

    dup_name = await session.execute(select(User).where(User.username == data.username))
    if dup_name.scalar_one_or_none():
        raise HTTPException(400, "用户名已被使用")
    dup_email = await session.execute(select(User).where(User.email == data.email))
    if dup_email.scalar_one_or_none():
        raise HTTPException(400, "邮箱已被注册")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login")
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    """支持用户名或邮箱登录"""
    result = await session.execute(
        select(User).where(
            or_(User.username == data.login, User.email == data.login)
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "账号或密码错误")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user),
    }


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user


class PasswordChange(SQLModel):
    old_password: str
    new_password: str


@router.patch("/password")
async def change_password(
    data: PasswordChange,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(400, "当前密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(400, "新密码至少 6 位")
    user.password_hash = hash_password(data.new_password)
    session.add(user)
    await session.commit()
    return {"message": "密码修改成功"}


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if data.username is not None:
        if len(data.username) < 2:
            raise HTTPException(400, "用户名至少 2 个字符")
        dup = await session.execute(
            select(User).where(User.username == data.username, User.id != user.id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(400, "用户名已被使用")
        user.username = data.username
    if data.bio is not None:
        user.bio = data.bio
    if data.avatar is not None:
        user.avatar = data.avatar

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
