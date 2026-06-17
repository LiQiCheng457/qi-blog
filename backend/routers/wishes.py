"""赛博许愿池 API"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy import func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import (
    Wish, WishResonance, WishRead, WishCreate, WishAdminRead, User,
)
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/wishes", tags=["许愿池"])

DAILY_LIMIT = 5
MAX_LEN = 60


async def _maybe_monthly_cleanup(session: AsyncSession) -> None:
    """月初懒清理：删除上月遗留的非种子愿望（含共鸣）。

    判定规则：取最早一条非种子愿望，若其 created_at 属于上月之前，则视为跨月，
    清空全部非种子愿望并清空对应共鸣。
    """
    now = datetime.utcnow()
    result = await session.execute(
        select(Wish)
        .where(Wish.is_seed == False)
        .order_by(Wish.created_at.asc())
        .limit(1)
    )
    oldest = result.scalar_one_or_none()
    if not oldest:
        return
    same_month = (
        oldest.created_at.year == now.year
        and oldest.created_at.month == now.month
    )
    if same_month:
        return

    # 找到所有非种子 wish_id
    ids_r = await session.execute(select(Wish.id).where(Wish.is_seed == False))
    ids = [i for (i,) in ids_r.all()]
    if ids:
        await session.execute(delete(WishResonance).where(WishResonance.wish_id.in_(ids)))
        await session.execute(delete(Wish).where(Wish.id.in_(ids)))
        await session.commit()


async def _has_resonated(session: AsyncSession, wish_id: int, user_id: int) -> bool:
    result = await session.execute(
        select(WishResonance.id).where(
            WishResonance.wish_id == wish_id,
            WishResonance.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


def _wish_to_read(wish: Wish, has_resonated: bool = False) -> WishRead:
    return WishRead(
        id=wish.id,
        content=wish.content,
        is_seed=wish.is_seed,
        resonance_count=wish.resonance_count,
        has_resonated=has_resonated,
        created_at=wish.created_at,
    )


# ── 公开：池子统计（围观用） ────────────────────────────────────
@router.get("/stats")
async def wish_stats(session: AsyncSession = Depends(get_session)):
    await _maybe_monthly_cleanup(session)
    total = (await session.execute(select(func.count()).select_from(Wish))).scalar_one()
    return {"total": total}


# ── 围观：随机捞一条（不需要登录） ─────────────────────────────
@router.get("/random", response_model=WishRead)
async def random_wish(
    exclude: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    await _maybe_monthly_cleanup(session)
    stmt = select(Wish)
    if exclude is not None:
        stmt = stmt.where(Wish.id != exclude)
    stmt = stmt.order_by(func.random()).limit(1)
    result = await session.execute(stmt)
    wish = result.scalar_one_or_none()
    if not wish:
        raise HTTPException(404, "池子是空的")
    return _wish_to_read(wish, has_resonated=False)


# ── 登录用户：投入一个愿望 ──────────────────────────────────────
@router.post("", response_model=WishRead, status_code=201)
async def create_wish(
    data: WishCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    text = data.content.strip()
    if not text:
        raise HTTPException(400, "愿望不能为空")
    if len(text) > MAX_LEN:
        raise HTTPException(400, f"愿望不能超过 {MAX_LEN} 字")

    await _maybe_monthly_cleanup(session)

    # 每日上限
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = (await session.execute(
        select(func.count()).select_from(Wish).where(
            Wish.user_id == user.id,
            Wish.created_at >= today_start,
        )
    )).scalar_one()
    if today_count >= DAILY_LIMIT:
        raise HTTPException(429, f"今天最多只能扔 {DAILY_LIMIT} 个愿望了，明天再来")

    wish = Wish(content=text, user_id=user.id, is_seed=False)
    session.add(wish)
    await session.commit()
    await session.refresh(wish)
    return _wish_to_read(wish, has_resonated=False)


# ── 登录用户：共鸣（去重，幂等） ────────────────────────────────
@router.post("/{wish_id}/resonate", response_model=WishRead)
async def resonate(
    wish_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(select(Wish).where(Wish.id == wish_id))
    wish = result.scalar_one_or_none()
    if not wish:
        raise HTTPException(404, "愿望不存在")

    # 已共鸣则直接返回
    if await _has_resonated(session, wish_id, user.id):
        return _wish_to_read(wish, has_resonated=True)

    session.add(WishResonance(wish_id=wish_id, user_id=user.id))
    wish.resonance_count = wish.resonance_count + 1
    session.add(wish)
    await session.commit()
    await session.refresh(wish)
    return _wish_to_read(wish, has_resonated=True)


# ── 管理员：列出所有愿望（按共鸣降序） ──────────────────────────
@router.get("/admin/list", response_model=list[WishAdminRead],
            dependencies=[Depends(get_current_admin)])
async def admin_list(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Wish).order_by(
            Wish.resonance_count.desc(), Wish.created_at.desc()
        )
    )
    wishes = result.scalars().all()

    # 拉用户名
    user_ids = list({w.user_id for w in wishes if w.user_id})
    user_map: dict[int, str] = {}
    if user_ids:
        users_r = await session.execute(select(User).where(User.id.in_(user_ids)))
        for u in users_r.scalars().all():
            user_map[u.id] = u.username

    return [
        WishAdminRead(
            id=w.id,
            content=w.content,
            user_id=w.user_id,
            username=user_map.get(w.user_id) if w.user_id else None,
            is_seed=w.is_seed,
            resonance_count=w.resonance_count,
            created_at=w.created_at,
        )
        for w in wishes
    ]


# ── 管理员：删除单条 ─────────────────────────────────────────
@router.delete("/admin/{wish_id}", dependencies=[Depends(get_current_admin)])
async def admin_delete(wish_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Wish).where(Wish.id == wish_id))
    wish = result.scalar_one_or_none()
    if not wish:
        raise HTTPException(404, "愿望不存在")
    await session.execute(delete(WishResonance).where(WishResonance.wish_id == wish_id))
    await session.delete(wish)
    await session.commit()
    return {"message": "已删除"}


# ── 管理员：一键清空非种子愿望 ────────────────────────────────
@router.delete("/admin/clear/all", dependencies=[Depends(get_current_admin)])
async def admin_clear(session: AsyncSession = Depends(get_session)):
    ids_r = await session.execute(select(Wish.id).where(Wish.is_seed == False))
    ids = [i for (i,) in ids_r.all()]
    if ids:
        await session.execute(delete(WishResonance).where(WishResonance.wish_id.in_(ids)))
        await session.execute(delete(Wish).where(Wish.id.in_(ids)))
        await session.commit()
    return {"cleared": len(ids)}
