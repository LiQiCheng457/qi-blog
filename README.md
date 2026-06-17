# Qi Blog

Qi Blog 是一个个人作品集博客项目，包含公开博客、项目展示、相册、用户登录、评论、AI 对话助手、工具箱小游戏和管理员后台。

线上预览：[https://www.optlab.space/blog/](https://www.optlab.space/blog/)

## 项目内容

- 公开站点：主页、关于、项目、相册、博客列表、文章详情。
- 内容功能：Markdown 文章渲染、代码高亮、文章目录、图片预览、评论。
- 用户功能：注册登录、个人资料、固定头像、修改密码。
- 互动功能：日历、番茄钟、今日运势、许愿池、2048 小游戏。
- AI 功能：登录用户可使用对话，支持历史记录和语音播放。
- 管理后台：文章、项目、相册、用户、评论、愿望、AI 聊天记录、下载包管理和数据看板。

## 技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- UnoCSS
- marked
- highlight.js
- ECharts / vue-echarts

后端：

- FastAPI
- SQLModel / SQLAlchemy async
- PostgreSQL
- JWT 鉴权
- httpx

## 目录结构

```text
frontend/   前端源码
backend/    后端源码
scripts/    项目脚本
```

## 本地运行

前端：

```powershell
cd frontend
npm install
npm run dev
```

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## 构建

```powershell
cd frontend
npm.cmd run build
```

## 部署说明

- 前端生产站点挂在 `/blog/` 下。
- `frontend/public/` 里的图片资源在 Vue 模板或 TS 代码里要通过 `assetUrl()` 生成最终路径。
- 服务器上的 `photos/` 和 `exes/` 是持久化资源目录，不随前端构建包上传或覆盖。
- 前端更新时只替换服务器上的静态 `dist/` 目录。
