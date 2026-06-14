from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Post, Comment, User
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

    return {
        "post_count":       post_count,
        "pub_count":        pub_count,
        "view_total":       view_total,
        "comment_count":    comment_count,
        "user_count":       user_count,
        "monthly_posts":    monthly_posts,
        "monthly_comments": monthly_comments,
        "top_posts":        top_posts,
    }
