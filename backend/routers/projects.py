from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from models import Project, ProjectRead, ProjectCreate, ProjectUpdate
from auth import get_current_admin

router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """获取项目列表（公开接口）"""
    stmt = select(Project)
    if category:
        stmt = stmt.where(Project.category == category)
    stmt = stmt.order_by(Project.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ProjectRead, dependencies=[Depends(get_current_admin)])
async def create_project(data: ProjectCreate, session: AsyncSession = Depends(get_session)):
    """创建项目（需要登录）"""
    project = Project(**data.model_dump())
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.patch("/{project_pk}", response_model=ProjectRead, dependencies=[Depends(get_current_admin)])
async def update_project(
    project_pk: int,
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新项目（需要登录，按数字主键）"""
    result = await session.execute(select(Project).where(Project.id == project_pk))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(project, key, value)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_pk}", dependencies=[Depends(get_current_admin)])
async def delete_project(project_pk: int, session: AsyncSession = Depends(get_session)):
    """删除项目（需要登录，按数字主键）"""
    result = await session.execute(select(Project).where(Project.id == project_pk))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    await session.delete(project)
    await session.commit()
    return {"message": "已删除"}
