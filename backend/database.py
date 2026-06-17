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
    """建表，并在首次启动时播种管理员账号和种子愿望"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await _seed_admin()
    await _seed_wishes()


async def _seed_admin():
    """如果数据库里还没有 admin，用 .env 里的配置创建一个"""
    from models import User
    from auth import hash_password

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
            # 若 .env 中的密码哈希与数据库不同，同步更新
            if existing.password_hash != admin_password_hash:
                existing.password_hash = admin_password_hash
                session.add(existing)
                await session.commit()
                print(f"[OK] 管理员密码哈希已同步更新")
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


SEED_WISHES = [
    "希望明天早餐有煎蛋",
    "希望这次需求别再改了",
    "希望今晚能睡个好觉",
    "希望下周不要开太多会",
    "希望快递今天能到",
    "希望老板今天心情好",
    "希望代码一次跑通",
    "希望周末不要被叫去加班",
    "希望今天的外卖不要洒",
    "希望永远不用回那封邮件",
    "希望路上不堵车",
    "希望今晚有人帮我洗碗",
    "希望测试通过，我太累了",
    "希望产品经理今天不在",
    "希望这个 bug 是别人的锅",
    "希望我的猫今天别踩键盘",
    "希望奶茶的糖不甜不腻刚刚好",
    "希望明天能早点下班",
    "希望天气凉一点，就一点点",
    "希望今天有好消息",
]


async def _seed_wishes():
    """首次启动写入 20 条种子愿望（is_seed=True）。已存在则跳过。"""
    from models import Wish
    from sqlmodel import select

    async with AsyncSessionLocal() as session:
        existing = (await session.execute(
            select(Wish).where(Wish.is_seed == True).limit(1)
        )).scalar_one_or_none()
        if existing:
            return
        for text in SEED_WISHES:
            session.add(Wish(content=text, is_seed=True))
        await session.commit()
        print(f"[OK] 已写入 {len(SEED_WISHES)} 条种子愿望")


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
