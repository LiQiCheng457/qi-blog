import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from database import init_db
from routers import posts, projects, auth, users, comments, admin, chat, photos, exes

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="起风了 API",
    description="祁的个人博客后端接口",
    version="1.0.0",
    lifespan=lifespan,
)

_cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:4173")
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(projects.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(photos.router)
app.include_router(exes.router)


@app.get("/")
async def root():
    return {"message": "起风了 API · 正在运行"}
