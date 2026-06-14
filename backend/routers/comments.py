from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Comment, CommentRead, CommentCreate, User
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/comments", tags=["评论"])


async def _enrich(comment: Comment, session: AsyncSession) -> CommentRead:
    result = await session.execute(select(User).where(User.id == comment.user_id))
    user = result.scalar_one_or_none()
    return CommentRead(
        id=comment.id,
        post_slug=comment.post_slug,
        user_id=comment.user_id,
        username=user.username if user else "已注销",
        avatar=user.avatar if user else None,
        role=user.role if user else "user",
        content=comment.content,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
    )


@router.get("/{post_slug}", response_model=list[CommentRead])
async def list_comments(post_slug: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Comment)
        .where(Comment.post_slug == post_slug)
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    return [await _enrich(c, session) for c in comments]


@router.post("/{post_slug}", response_model=CommentRead, status_code=201)
async def create_comment(
    post_slug: str,
    data: CommentCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if not data.content.strip():
        raise HTTPException(400, "评论内容不能为空")
    if len(data.content) > 1000:
        raise HTTPException(400, "评论不能超过 1000 字")

    comment = Comment(
        post_slug=post_slug,
        user_id=user.id,
        content=data.content.strip(),
        parent_id=data.parent_id,
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return await _enrich(comment, session)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(404, "评论不存在")
    if comment.user_id != user.id and user.role != "admin":
        raise HTTPException(403, "无权删除他人评论")
    await session.delete(comment)
    await session.commit()
    return {"message": "已删除"}


@router.delete("/admin/{comment_id}", dependencies=[Depends(get_current_admin)])
async def admin_delete_comment(comment_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(404, "评论不存在")
    await session.delete(comment)
    await session.commit()
    return {"message": "已删除"}
