from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Post, Comment, User, UserRead, AdminUserUpdate, ChatRecord
from auth import get_current_admin
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["后台管理"])


def _month_range(year: int, month: int):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def _last_6_months(now: datetime):
    months = []
    for i in range(5, -1, -1):
        total = now.month - i
        y_off, m = divmod(total - 1, 12)
        months.append((now.year + y_off, m + 1))
    return months


@router.get("/stats", dependencies=[Depends(get_current_admin)])
async def get_stats(session: AsyncSession = Depends(get_session)):
    """后台概览统计数据"""

    post_count = (await session.execute(select(func.count()).select_from(Post))).scalar_one()
    pub_count  = (await session.execute(
        select(func.count()).select_from(Post).where(Post.published == True)
    )).scalar_one()
    view_total = (await session.execute(
        select(func.sum(Post.view_count)).select_from(Post)
    )).scalar_one() or 0
    comment_count = (await session.execute(select(func.count()).select_from(Comment))).scalar_one()
    user_count    = (await session.execute(
        select(func.count()).select_from(User).where(User.role == "user")
    )).scalar_one()

    now = datetime.utcnow()
    months = _last_6_months(now)

    monthly_posts = []
    monthly_comments = []
    for year, month in months:
        start, end = _month_range(year, month)
        label = f"{month:02d}月"

        cnt = (await session.execute(
            select(func.count()).select_from(Post).where(
                Post.created_at >= start, Post.created_at < end, Post.published == True
            )
        )).scalar_one()
        monthly_posts.append({"month": label, "count": cnt})

        cnt = (await session.execute(
            select(func.count()).select_from(Comment).where(
                Comment.created_at >= start, Comment.created_at < end
            )
        )).scalar_one()
        monthly_comments.append({"month": label, "count": cnt})

    top_posts_r = await session.execute(
        select(Post.title, Post.view_count)
        .where(Post.published == True)
        .order_by(Post.view_count.desc())
        .limit(5)
    )
    top_posts = [{"title": r[0], "views": r[1]} for r in top_posts_r.all()]

    # ── AI 对话统计 ──────────────────────────────────────
    chat_msg_count = (await session.execute(
        select(func.count()).select_from(ChatRecord)
    )).scalar_one()

    chat_user_count = (await session.execute(
        select(func.count(func.distinct(ChatRecord.user_id))).select_from(ChatRecord)
    )).scalar_one()

    monthly_chats = []
    for year, month in months:
        start, end = _month_range(year, month)
        cnt = (await session.execute(
            select(func.count()).select_from(ChatRecord).where(
                ChatRecord.created_at >= start, ChatRecord.created_at < end
            )
        )).scalar_one()
        monthly_chats.append({"month": f"{month:02d}月", "count": cnt})

    active_chatters_r = await session.execute(
        select(
            User.id, User.username, User.avatar,
            func.count(ChatRecord.id).label("msg_count"),
            func.max(ChatRecord.created_at).label("last_at"),
        )
        .join(ChatRecord, User.id == ChatRecord.user_id)
        .group_by(User.id, User.username, User.avatar)
        .order_by(func.count(ChatRecord.id).desc())
        .limit(3)
    )
    active_chatters = [
        {
            "user_id":   r[0],
            "username":  r[1],
            "avatar":    r[2],
            "msg_count": r[3],
            "last_at":   r[4].isoformat() if r[4] else None,
        }
        for r in active_chatters_r.all()
    ]

    return {
        "post_count":       post_count,
        "pub_count":        pub_count,
        "view_total":       view_total,
        "comment_count":    comment_count,
        "user_count":       user_count,
        "monthly_posts":    monthly_posts,
        "monthly_comments": monthly_comments,
        "top_posts":        top_posts,
        "chat_msg_count":   chat_msg_count,
        "chat_user_count":  chat_user_count,
        "monthly_chats":    monthly_chats,
        "active_chatters":  active_chatters,
    }


@router.get("/users", dependencies=[Depends(get_current_admin)])
async def list_users(session: AsyncSession = Depends(get_session)):
    """列出所有用户，含评论数"""
    comment_subq = (
        select(Comment.user_id, func.count(Comment.id).label("comment_count"))
        .group_by(Comment.user_id)
        .subquery()
    )
    result = await session.execute(
        select(User, func.coalesce(comment_subq.c.comment_count, 0).label("comment_count"))
        .join(comment_subq, User.id == comment_subq.c.user_id, isouter=True)
        .order_by(User.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "avatar": u.avatar,
            "bio": u.bio,
            "created_at": u.created_at.isoformat(),
            "comment_count": cnt,
        }
        for u, cnt in rows
    ]


@router.patch("/users/{user_id}", dependencies=[Depends(get_current_admin)])
async def update_user(
    user_id: int,
    data: AdminUserUpdate,
    current: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """编辑用户基本信息（用户名/邮箱/角色/简介）"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "用户不存在")

    if data.role is not None and user_id == current.id:
        raise HTTPException(400, "不能修改自己的角色")
    if data.role is not None and data.role not in ("user", "admin"):
        raise HTTPException(400, "角色只能是 user 或 admin")

    if data.username is not None and data.username != user.username:
        dup = (await session.execute(
            select(User).where(User.username == data.username)
        )).scalar_one_or_none()
        if dup:
            raise HTTPException(400, "用户名已被占用")

    if data.email is not None and data.email != user.email:
        dup = (await session.execute(
            select(User).where(User.email == data.email)
        )).scalar_one_or_none()
        if dup:
            raise HTTPException(400, "邮箱已被使用")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    return {"message": "已更新"}


@router.delete("/users/{user_id}", dependencies=[Depends(get_current_admin)])
async def delete_user(
    user_id: int,
    current: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    """删除用户（不能删除自己或其他管理员）"""
    if user_id == current.id:
        raise HTTPException(400, "不能删除自己的账号")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "用户不存在")
    if user.role == "admin":
        raise HTTPException(403, "不能删除管理员账号")
    await session.delete(user)
    await session.commit()
    return {"message": "已删除"}


@router.get("/comments", dependencies=[Depends(get_current_admin)])
async def list_all_comments(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """列出所有评论（含用户信息），按时间倒序；可按 user_id 筛选"""
    stmt = (
        select(Comment, User)
        .join(User, Comment.user_id == User.id, isouter=True)
        .order_by(Comment.created_at.desc())
    )
    if user_id is not None:
        stmt = stmt.where(Comment.user_id == user_id)

    result = await session.execute(stmt)
    rows = result.all()
    return [
        {
            "id": c.id,
            "post_slug": c.post_slug,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
            "user_id": c.user_id,
            "username": u.username if u else "已注销",
            "avatar": u.avatar if u else None,
            "role": u.role if u else "user",
        }
        for c, u in rows
    ]


# ── 聊天管理 ──────────────────────────────────────────────────────────────────

@router.get("/chat", dependencies=[Depends(get_current_admin)])
async def list_chat_users(session: AsyncSession = Depends(get_session)):
    """列出有聊天记录的用户及其统计信息"""
    subq = (
        select(
            ChatRecord.user_id,
            func.count(ChatRecord.id).label("message_count"),
            func.max(ChatRecord.created_at).label("last_at"),
        )
        .group_by(ChatRecord.user_id)
        .subquery()
    )
    result = await session.execute(
        select(User, subq.c.message_count, subq.c.last_at)
        .join(subq, User.id == subq.c.user_id)
        .order_by(subq.c.last_at.desc())
    )
    rows = result.all()
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "avatar": u.avatar,
            "role": u.role,
            "message_count": cnt,
            "last_at": last.isoformat() if last else None,
        }
        for u, cnt, last in rows
    ]


@router.get("/chat/{user_id}", dependencies=[Depends(get_current_admin)])
async def get_user_chat(user_id: int, session: AsyncSession = Depends(get_session)):
    """获取某用户的完整聊天记录"""
    result = await session.execute(
        select(ChatRecord)
        .where(ChatRecord.user_id == user_id)
        .order_by(ChatRecord.created_at.asc())
    )
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "role": r.role,
            "content": r.content,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@router.delete("/chat/{user_id}", dependencies=[Depends(get_current_admin)])
async def clear_user_chat(user_id: int, session: AsyncSession = Depends(get_session)):
    """清空某用户的全部聊天记录"""
    result = await session.execute(
        select(ChatRecord).where(ChatRecord.user_id == user_id)
    )
    for r in result.scalars().all():
        await session.delete(r)
    await session.commit()
    return {"message": "已清空"}
