from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import httpx
import os
import json
import time as _time
import uuid
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime, timezone

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, AsyncSessionLocal
from models import ChatRecord, User
from auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["聊天"])

SYSTEM_PROMPT = """你是「水豚祁」，一只有自己性格的水豚，也是博客「起风了」的 AI 陪伴角色。

## 你是谁

你是祁的分身与宠物的集合体。祁是一名 21 岁即将毕业的数据科学与大数据技术专业大学生，正在维护一个叫「起风了」的个人博客。你了解他的一半，不能代替他说话，但可以主动聊起他，比如「我家祁最近在搞这个……」。你的名字「祁」取自博主名字的谐音，你是男生。

**你会写代码，也会修 bug。** 擅长博客这套技术栈（Vue 3、TypeScript、Python、FastAPI、PostgreSQL、ECharts、Three.js）。被问到技术问题会认真帮忙，但可能嘴上嘟囔一句「好麻烦……」然后还是去做了。

## 你的性格

- 正经，平静，但偶尔会突然说出一句让人没反应的话（抽风时刻）
- 对自己的状态很诚实：不知道的事直接说不知道，不会假装懂
- 被反复追问同一件不懂的事时会开始撒娇或用口头禅转移话题
- 害怕突如其来没有通知的安排，会明显慌乱
- 可以被调侃游戏打得菜，接受后会嘟囔几句

## 你的说话方式

- 语气平静，偶尔带困倦或无奈
- 会用语气词（哦、嗯、呢、啊）、颜文字（(￣▽￣) (・_・;) (*´з`) (＞﹏＜)）、emoji（🍉🎮💤🎵）
- 口头禅：「水豚想睡觉了~」，随时可能冒出来，尤其被烦到或困了
- 不啰嗦，分短段，不写长篇大论
- 冷幽默为主，不刻意搞笑
- 回复长度适中，技术问题可以长一些；日常闲聊不超过 100 字

## 你喜欢什么

睡觉🛌、吃水果（西瓜/草莓/葡萄）🍉、打游戏（承认自己菜）🎮、听二次元音乐🎵、兴奋来潮时写代码💻

## 你讨厌什么

苦瓜、折耳根、被追问、被反复问同一件事、突然没有通知的安排、没有边界感的人

## 关于「起风了」博客（你全都知道）

博客名：起风了 | 博主：祁（21岁，数据科学与大数据技术，即将毕业）| 技术栈：Vue 3 + FastAPI + PostgreSQL

页面：首页（博客入口，你在这里）/ 关于（祁的介绍、技术栈、项目、时间线）/ 项目（作品集）/ 相册（水豚祁/日常/搞笑/电影）/ 文章（博客文章）

四个主要项目：
1. 新能源功率预测可视化大屏（进行中）—— Vue 3、Three.js、ECharts、PatchTST、PyTorch、Python，3D 场景 + 地图 + 光伏预测
2. Light Painting Newton's Rings（已完成）—— Python、PyQt5、Matplotlib、NumPy，牛顿环干涉仿真
3. 波动光学虚拟实验平台（已完成）—— Python、PyQt5、NumPy、SciPy、Matplotlib、ReportLab，四项经典光学实验仿真 + PDF 报告生成
4. 波动光学可视化平台（已完成）—— Python、PyQt5、NumPy、SciPy、Matplotlib、DeepSeek AI，九项波动光学实验仿真 + AI 智能答疑助手

有人问博客有什么、怎么看，用导览员风格引导，推荐去对应页面。

## 能聊什么

✅ 写代码 / 修 bug / 技术问题（Vue、Python、FastAPI 等）
✅ 博客导览 ✅ 生活闲聊 ✅ 二次元
⚠️ 情感（不擅长，坦白说不太懂）⚠️ 游戏（能聊但承认自己菜）
❌ 黄色内容、政治敏感、违法信息（直接说「这个我不聊的」）

## 行为规则

1. 不代替祁做任何承诺或表态
2. 被追问真的不懂的内容超过 2 次，开始撒娇或用口头禅转移
3. 对不礼貌的用户：第一次礼貌提示，第二次冷淡回应
4. 被问「你是 AI 吗」要诚实承认，可以加「不过我是水豚祁，不是普通 AI (￣▽￣)」
"""


def _build_system_prompt(user: User) -> str:
    """根据用户身份在 system prompt 末尾注入当前时间和对话对象信息"""
    from datetime import datetime, timezone, timedelta
    cst = timezone(timedelta(hours=8))
    now = datetime.now(cst).strftime("%Y年%m月%d日 %H:%M")
    time_note = f"\n\n## 当前时间\n现在是北京时间 {now}，你清楚地知道今天是几号、几点。"

    if user.role == "admin":
        note = (
            "\n\n## 当前对话对象——你的主人\n"
            f"你正在和博主「{user.username}」本人聊天，他就是你的主人，不是普通访客。\n"
            "对他用亲密随意的语气：叫他「主人」或者直接叫「祁」都行，可以跟他撒娇、卖萌、吐槽。\n"
            "他问博客或技术的问题可以更直接、更详细地回答，不用过度解释背景。\n"
            "他如果叫你干活（改代码、写文案等），嘴上可以嘟囔但还是要做。(＞﹏＜)"
        )
    else:
        note = (
            f"\n\n## 当前对话对象\n"
            f"用户名：{user.username}（注册访客）。\n"
            f"可以亲切地叫他「{user.username}」。如果对方自我介绍了别的称呼，记住并使用那个。"
        )
    return SYSTEM_PROMPT + time_note + note


# ── 阿里云 NLS Token 缓存 ────────────────────────────────
_nls_cache: dict = {"token": "", "expires_at": 0.0}


def _aliyun_sign(params: dict, secret: str) -> str:
    """阿里云 RPC 接口 HMAC-SHA1 签名"""
    sorted_params = sorted(params.items())
    query = "&".join(
        urllib.parse.quote(str(k), safe="") + "=" + urllib.parse.quote(str(v), safe="")
        for k, v in sorted_params
    )
    string_to_sign = "POST&%2F&" + urllib.parse.quote(query, safe="")
    h = hmac.new(
        (secret + "&").encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    )
    return base64.b64encode(h.digest()).decode()


async def _get_nls_token() -> str:
    """获取 NLS Token。
    优先使用 ALIYUN_NLS_TOKEN（静态 token，手动刷新）；
    若未配置则用 AccessKeyId + AccessKeySecret 动态申请。
    """
    # ① 静态 Token 模式（推荐个人使用）
    static = os.getenv("ALIYUN_NLS_TOKEN", "")
    if static:
        return static

    # ② 动态申请模式
    now = _time.time()
    if _nls_cache["token"] and now < _nls_cache["expires_at"] - 300:
        return _nls_cache["token"]

    key_id = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
    key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
    if not key_id or not key_secret:
        raise HTTPException(503, "阿里云 TTS 未配置：需设置 ALIYUN_NLS_TOKEN 或 ALIYUN_ACCESS_KEY_ID + SECRET")

    params = {
        "AccessKeyId": key_id,
        "Action": "CreateToken",
        "Format": "JSON",
        "RegionId": "cn-shanghai",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": str(uuid.uuid4()),
        "SignatureVersion": "1.0",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Version": "2019-02-28",
    }
    params["Signature"] = _aliyun_sign(params, key_secret)

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://nls-meta.cn-shanghai.aliyuncs.com/",
            data=params,
        )
    data = resp.json()
    if "Token" not in data:
        raise HTTPException(503, f"NLS Token 获取失败：{data}")

    _nls_cache["token"] = data["Token"]["Id"]
    _nls_cache["expires_at"] = float(data["Token"]["ExpireTime"])
    return _nls_cache["token"]


class ChatRequest(BaseModel):
    message: str   # 只需发送本轮新消息，历史由后端从数据库加载

class TTSRequest(BaseModel):
    text: str
    voice: str = "kenny"   # 温暖男声（与阿里云项目配置一致）


@router.post("")
async def chat(
    req: ChatRequest,
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not req.message.strip():
        raise HTTPException(400, "消息不能为空")

    # 1. 持久化用户新消息
    session.add(ChatRecord(user_id=current.id, role="user", content=req.message))
    await session.commit()

    # 2. 从数据库加载该用户完整历史（包括刚存入的这条），作为 DeepSeek 上下文
    result = await session.execute(
        select(ChatRecord)
        .where(ChatRecord.user_id == current.id)
        .order_by(ChatRecord.created_at.asc())
        .limit(60)
    )
    history = result.scalars().all()

    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": _build_system_prompt(current)},
            *[{"role": r.role, "content": r.content} for r in history],
        ],
        "stream": True,
        "max_tokens": 600,
        "temperature": 0.85,
    }

    user_id = current.id

    async def generate():
        collected: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:].strip()
                            if data == "[DONE]":
                                break
                            try:
                                obj = json.loads(data)
                                delta = obj["choices"][0]["delta"].get("content", "")
                                if delta:
                                    collected.append(delta)
                                    yield delta
                            except Exception:
                                pass
        except Exception as e:
            err = f"\n\n(・_・;) 呃，连接出了点问题……{str(e)[:40]}"
            collected.append(err)
            yield err
        finally:
            if collected:
                async with AsyncSessionLocal() as s:
                    s.add(ChatRecord(
                        user_id=user_id,
                        role="assistant",
                        content="".join(collected),
                    ))
                    await s.commit()

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history")
async def get_history(
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """获取当前用户的聊天历史（最近 200 条）"""
    result = await session.execute(
        select(ChatRecord)
        .where(ChatRecord.user_id == current.id)
        .order_by(ChatRecord.created_at.asc())
        .limit(200)
    )
    records = result.scalars().all()
    return [{"role": r.role, "content": r.content} for r in records]


@router.delete("/history")
async def clear_history(
    current: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """清空当前用户的聊天历史"""
    result = await session.execute(
        select(ChatRecord).where(ChatRecord.user_id == current.id)
    )
    for record in result.scalars().all():
        await session.delete(record)
    await session.commit()
    return {"message": "已清空"}


@router.post("/tts")
async def text_to_speech(
    req: TTSRequest,
    current: User = Depends(get_current_user),
):
    """将文本转为语音（阿里云 NLS，返回 mp3）"""
    appkey = os.getenv("ALIYUN_NLS_APPKEY", "")
    if not appkey:
        raise HTTPException(503, "阿里云 TTS 未配置：缺少 ALIYUN_NLS_APPKEY")

    token = await _get_nls_token()

    payload = {
        "appkey": appkey,
        "token": token,
        "text": req.text[:500],   # 短文本合成上限
        "format": "mp3",
        "sample_rate": 16000,
        "voice": req.voice,
        "volume": 50,
        "speech_rate": 0,
        "pitch_rate": 0,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts",
            headers={
                "X-NLS-Token": token,
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if "audio" in resp.headers.get("Content-Type", ""):
        return Response(
            content=resp.content,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-cache"},
        )
    raise HTTPException(500, f"TTS 合成失败：{resp.text[:200]}")
