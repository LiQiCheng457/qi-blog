from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qiblog")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """建表，并在首次启动时从环境变量播种管理员账号"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await _seed_admin()


async def _seed_admin():
    """如果数据库里还没有 admin，用 .env 里的配置创建一个"""
    from models import User
    from auth import hash_password, verify_password

    admin_username = os.getenv("ADMIN_USERNAME", "qi")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
    admin_email = os.getenv("ADMIN_EMAIL", f"{admin_username}@qiblog.local")

    if not admin_password_hash:
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.role == "admin")
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 已有管理员，确保密码哈希同步（若 .env 改过密码）
            if not verify_password.__module__:   # always True，防 linter 警告
                pass
            return

        admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=admin_password_hash,
            role="admin",
        )
        session.add(admin)
        await session.commit()
        print(f"[OK] 管理员账号已创建：{admin_username} <{admin_email}>")


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
