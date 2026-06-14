from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import os
import json

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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@router.post("")
async def chat(req: ChatRequest):
    api_key = os.getenv("DEEPSEEK_API_KEY", "")

    # 最多取最近 60 条，避免超出上下文限制
    messages = req.messages[-60:] if len(req.messages) > 60 else req.messages

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *[{"role": m.role, "content": m.content} for m in messages],
        ],
        "stream": True,
        "max_tokens": 600,
        "temperature": 0.85,
    }

    async def generate():
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
                                    yield delta
                            except Exception:
                                pass
        except Exception as e:
            yield f"\n\n(・_・;) 呃，连接出了点问题……{str(e)[:40]}"

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
