from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Post, PostRead, PostCreate, PostUpdate
from auth import get_current_admin

router = APIRouter(prefix="/api/posts", tags=["文章"])


@router.get("", response_model=list[PostRead])
async def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    tag: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """获取文章列表（公开接口）"""
    stmt = select(Post).where(Post.published == True)
    if tag:
        stmt = stmt.where(Post.tags.contains(tag))
    stmt = stmt.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{slug}", response_model=PostRead)
async def get_post(slug: str, session: AsyncSession = Depends(get_session)):
    """获取单篇文章（公开接口），同时累计阅读量"""
    result = await session.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    post.view_count += 1
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.post("", response_model=PostRead, dependencies=[Depends(get_current_admin)])
async def create_post(data: PostCreate, session: AsyncSession = Depends(get_session)):
    """创建文章（需要登录）"""
    existing = await session.execute(select(Post).where(Post.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="slug 已存在")
    post = Post(**data.model_dump())
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.patch("/{slug}", response_model=PostRead, dependencies=[Depends(get_current_admin)])
async def update_post(slug: str, data: PostUpdate, session: AsyncSession = Depends(get_session)):
    """更新文章（需要登录）"""
    result = await session.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(post, key, val)
    from datetime import datetime
    post.updated_at = datetime.utcnow()
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.get("/{slug}/adjacent")
async def adjacent_posts(slug: str, session: AsyncSession = Depends(get_session)):
    """获取指定文章的上一篇和下一篇（按创建时间排序）"""
    result = await session.execute(select(Post).where(Post.slug == slug, Post.published == True))
    current = result.scalar_one_or_none()
    if not current:
        raise HTTPException(404, "文章不存在")

    prev_r = await session.execute(
        select(Post).where(Post.published == True, Post.created_at < current.created_at)
        .order_by(Post.created_at.desc()).limit(1)
    )
    next_r = await session.execute(
        select(Post).where(Post.published == True, Post.created_at > current.created_at)
        .order_by(Post.created_at.asc()).limit(1)
    )
    prev_post = prev_r.scalar_one_or_none()
    next_post = next_r.scalar_one_or_none()
    return {
        "prev": {"slug": prev_post.slug, "title": prev_post.title} if prev_post else None,
        "next": {"slug": next_post.slug, "title": next_post.title} if next_post else None,
    }


@router.delete("/{slug}", dependencies=[Depends(get_current_admin)])
async def delete_post(slug: str, session: AsyncSession = Depends(get_session)):
    """删除文章（需要登录）"""
    result = await session.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    await session.delete(post)
    await session.commit()
    return {"message": "已删除"}
