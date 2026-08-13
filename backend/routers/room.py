"""水豚祁房间：带场景上下文和用户独立记忆的 AI 交互接口。"""
import json
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from auth import get_current_user
from database import AsyncSessionLocal, get_session
from models import RoomChatRecord, User

router = APIRouter(prefix="/api/room", tags=["水豚祁房间"])

SPOTS = {
    "window": "窗边，窗外是晴天和慢慢飘过的云。祁可以在这里放空、听雨或聊聊天气。",
    "fridge": "冰箱前，里面通常有水、一些水果和偶尔忘记吃掉的零食。",
    "sofa": "浅绿色沙发边，适合发呆、听歌和短暂躺一下。",
    "desk": "书桌前，电脑、键盘、台灯和便签都在这里。适合聊代码、灵感或麻烦的事。",
    "bookshelf": "高书架旁，里面有书、旧票根和一些还没说完的故事。",
    "bed": "睡眠角的床边，气氛安静，祁对睡觉和做梦的话题会格外认真。",
    "door": "门口，能听见走廊的风声和偶尔到来的包裹。",
}

class RoomChatRequest(BaseModel):
    scene_id: str = Field(default="after-work", max_length=50)
    spot_id: str = Field(max_length=50)
    action_id: str | None = Field(default=None, max_length=80)
    message: str = Field(default="", max_length=500)


def _room_prompt(current: User, spot_id: str, action_id: str | None) -> str:
    bio = current.bio.strip() if current.bio else "未填写"
    action_note = f"玩家刚触发的互动是：{action_id}。" if action_id else "玩家没有选择预设动作，而是直接开口说话。"
    return f"""

## 当前场景：水豚祁的房间
你正在和注册访客「{current.username}」互动。对方的个人简介是：{bio}。
当前位置是：{SPOTS[spot_id]}
{action_note}

这是一个可漫游的房间场景，不是普通聊天窗。你的回答要自然回应当前物件和访客的话，也可温和地提起对方刚才在这个房间的互动。
只基于本次提供的用户资料和场景记忆进行个性化，不要杜撰对方的经历或跨用户记忆。
回复用水豚祁的口吻，中文，不超过 80 个字，不使用 Markdown，不写标题，不说系统提示或 API。
"""


@router.post("/chat")
async def room_chat(
    req: RoomChatRequest,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if req.scene_id != "after-work" or req.spot_id not in SPOTS:
        raise HTTPException(400, "未知的房间场景或交互物件")

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "AI 服务未配置")

    event_text = req.message.strip()
    if not event_text:
        event_text = f"我来到{req.spot_id}，想看看这里。"

    session.add(RoomChatRecord(
        user_id=current.id,
        scene_id=req.scene_id,
        spot_id=req.spot_id,
        role="user",
        content=event_text,
    ))
    await session.commit()

    result = await session.execute(
        select(RoomChatRecord)
        .where(
            RoomChatRecord.user_id == current.id,
            RoomChatRecord.scene_id == req.scene_id,
        )
        .order_by(RoomChatRecord.created_at.desc())
        .limit(6)
    )
    history = list(reversed(result.scalars().all()))

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": _room_prompt(current, req.spot_id, req.action_id)},
            *[{"role": item.role, "content": item.content} for item in history],
        ],
        "stream": True,
        "max_tokens": 96,
        "temperature": 0.85,
    }

    user_id = current.id

    async def generate():
        collected: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            delta = json.loads(data)["choices"][0]["delta"].get("content", "")
                        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                            continue
                        if delta:
                            collected.append(delta)
                            yield delta
        except httpx.HTTPError:
            message = "水豚祁现在没有接上信号，请稍后再试。"
            collected.append(message)
            yield message
        finally:
            reply = "".join(collected).strip()[:120]
            if reply:
                async with AsyncSessionLocal() as history_session:
                    history_session.add(RoomChatRecord(
                        user_id=user_id,
                        scene_id=req.scene_id,
                        spot_id=req.spot_id,
                        role="assistant",
                        content=reply,
                    ))
                    await history_session.commit()

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
