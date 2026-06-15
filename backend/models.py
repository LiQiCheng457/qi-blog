from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from typing import Optional
from datetime import datetime


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    summary: str
    content: str = Field(sa_column=Column(Text))
    tags: str = Field(default="")
    reading_time: int = Field(default=5)
    cover: Optional[str] = None
    published: bool = Field(default=True)
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str = Field(unique=True, index=True)
    name: str
    description: str = Field(sa_column=Column(Text))
    tech_stack: str = Field(default="")
    category: str
    github: Optional[str] = None
    url: Optional[str] = None
    download: Optional[str] = None
    cover: Optional[str] = None
    featured: bool = Field(default=False)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Photo(SQLModel, table=True):
    __tablename__ = "photos"
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    alt: str = Field(default="")
    tag: str = Field(default="")
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    """统一用户表：role=admin 为博主，role=user 为普通读者"""
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")        # "user" | "admin"
    avatar: Optional[str] = None             # 头像 URL
    bio: Optional[str] = None                # 个人简介
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    id: Optional[int] = Field(default=None, primary_key=True)
    post_slug: str = Field(index=True)
    user_id: int = Field(foreign_key="users.id")
    content: str = Field(sa_column=Column(Text))
    parent_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRecord(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str                                          # "user" | "assistant"
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Pydantic 响应 / 请求模型 ─────────────────────────────────────

class PostRead(SQLModel):
    id: int; slug: str; title: str; summary: str; content: str
    tags: str; reading_time: int; cover: Optional[str]
    published: bool; view_count: int; created_at: datetime; updated_at: datetime

class PostCreate(SQLModel):
    slug: str; title: str; summary: str; content: str
    tags: str = ""; reading_time: int = 5; cover: Optional[str] = None; published: bool = True

class PostUpdate(SQLModel):
    title: Optional[str] = None; summary: Optional[str] = None
    content: Optional[str] = None; tags: Optional[str] = None
    reading_time: Optional[int] = None; cover: Optional[str] = None; published: Optional[bool] = None


class ProjectRead(SQLModel):
    id: int; project_id: str; name: str; description: str; tech_stack: str
    category: str; github: Optional[str]; url: Optional[str]; download: Optional[str]; cover: Optional[str]
    featured: bool; status: str; created_at: datetime

class ProjectCreate(SQLModel):
    project_id: str; name: str; description: str; tech_stack: str = ""
    category: str; github: Optional[str] = None; url: Optional[str] = None
    download: Optional[str] = None; cover: Optional[str] = None
    featured: bool = False; status: str = "active"

class ProjectUpdate(SQLModel):
    name: Optional[str] = None; description: Optional[str] = None
    tech_stack: Optional[str] = None; category: Optional[str] = None
    github: Optional[str] = None; url: Optional[str] = None
    download: Optional[str] = None; cover: Optional[str] = None
    featured: Optional[bool] = None; status: Optional[str] = None


class UserRead(SQLModel):
    id: int; username: str; email: str; role: str
    avatar: Optional[str]; bio: Optional[str]; created_at: datetime

class UserRegister(SQLModel):
    username: str; email: str; password: str

class UserLogin(SQLModel):
    login: str      # 用户名 或 邮箱
    password: str

class UserUpdate(SQLModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class AdminUserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None


class CommentRead(SQLModel):
    id: int; post_slug: str; user_id: int
    username: str; avatar: Optional[str]; role: str
    content: str; parent_id: Optional[int]; created_at: datetime

class CommentCreate(SQLModel):
    content: str; parent_id: Optional[int] = None


class PhotoRead(SQLModel):
    id: int; url: str; alt: str; tag: str; sort_order: int; created_at: datetime

class PhotoUpdate(SQLModel):
    alt: Optional[str] = None
    tag: Optional[str] = None
    sort_order: Optional[int] = None
