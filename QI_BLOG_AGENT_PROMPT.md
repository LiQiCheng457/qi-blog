# 起风了个人作品集博客 - Agent 开发手册

> 适用对象：接手本仓库的开发 Agent、维护者和代码生成助手。
> 当前文档按现有项目状态整理，不再描述早期 mock-only 方案。

## 1. 项目定位

`起风了` 是一个个人作品集博客，包含公开站点、用户登录资料页、评论能力、AI 对话助手（水豚祁）和博主管理后台。

核心气质：

- 温暖、克制、有风感。
- 以水豚吉祥物"祁"为视觉 IP。
- 公开页面偏博客和作品集，后台页面偏工具化、信息密度高。

开发原则：

- 先读现有代码，再改动。
- 优先沿用当前目录、API、组件和 CSS token。
- 不做无关重构，不引入未经确认的新框架。
- 所有提交前必须跑 `npm.cmd run build`，后端改动至少做语法/接口级检查。

## 2. 技术栈

### 前端

- Vue 3 + `<script setup>`
- TypeScript
- Vite 5
- Vue Router 4
- Pinia
- UnoCSS
- marked
- highlight.js
- ECharts / vue-echarts

### 后端

- FastAPI
- SQLModel
- SQLAlchemy async
- asyncpg / psycopg2-binary
- python-jose JWT
- passlib bcrypt
- httpx（用于调用外部 API：DeepSeek、阿里云 NLS）
- PostgreSQL

## 3. 当前目录结构

```text
.
├─ frontend/
│  ├─ public/
│  │  ├─ animations/          # 水豚动图资源，WebP/GIF
│  │  ├─ avatars/             # 用户资料页固定头像库
│  │  ├─ tiles/               # 2048 水豚 AI 插画 tile（18 张 256×256 PNG + 源图 grid1/grid2）
│  │  └─ tools/               # 工具箱页面所需静态资源
│  ├─ src/
│  │  ├─ api/                 # 前端 API 封装（统一通过 client.ts）
│  │  ├─ assets/              # 页面静态图片资源
│  │  ├─ components/          # 通用组件（含 LoadingOverlay、ChatWidget、工具 Widget）
│  │  ├─ composables/         # 组合式逻辑
│  │  ├─ data/                # 本地补充数据
│  │  ├─ router/              # 路由与守卫（守卫在模块级注册）
│  │  ├─ stores/              # Pinia stores
│  │  ├─ styles/tokens.css    # 全局设计变量与基础样式
│  │  ├─ types/               # 前端类型
│  │  ├─ utils/assets.ts      # assetUrl() 工具函数，处理 Vite base 前缀
│  │  └─ views/
│  │     ├─ games/            # 游戏页面（Blog2048View.vue 等）
│  │     └─ ...               # 其他页面和后台页面
│  ├─ package.json
│  └─ vite.config.ts
├─ backend/
│  ├─ routers/                # FastAPI routers（posts/projects/users/comments/photos/chat/admin/wishes）
│  ├─ scripts/                # 初始化、导入、云端配置脚本
│  ├─ auth.py                 # JWT 与鉴权工具
│  ├─ database.py             # 异步数据库连接与初始化种子
│  ├─ main.py                 # FastAPI 应用入口
│  └─ models.py               # SQLModel 表与请求响应模型
├─ scripts/
│  └─ tile-crop/              # 图片裁剪脚本（crop_grid1.py / crop_grid2.py）
├─ QI_BLOG_AGENT_PROMPT.md
├─ PROGRESS.md
└─ DEPLOY.md
```

## 4. 路由与页面

### 公开前台

| 路由 | 页面 | 说明 |
|---|---|---|
| `/` | `HomeView.vue` | 首页，Hero、精选项目、文章预览 |
| `/about` | `AboutView.vue` | 关于页 |
| `/projects` | `ProjectsView.vue` | 项目列表与分类筛选 |
| `/blog` | `BlogView.vue` | 文章列表、搜索、标签筛选 |
| `/blog/:slug` | `PostView.vue` | 文章详情、Markdown、目录、评论 |
| `/profile` | `ProfileView.vue` | 登录用户资料页、固定头像选择、改密码 |
| `/tools` | `ToolsView.vue` | 工具箱：日历/番茄钟/迷信指数/赛博许愿池，双列瀑布流布局 |
| `/games` | `GamesView.vue` | 游戏大厅，卡片列表 |
| `/games/2048` | `games/Blog2048View.vue` | 2048 起风了版，水豚 AI 插画 tile |
| fallback | `NotFoundView.vue` | 404 |

### 后台

| 路由 | 页面 | 权限 |
|---|---|---|
| `/admin` | `AdminDashboard.vue` | admin |
| `/admin/posts` | `AdminPosts.vue` | admin |
| `/admin/posts/new` | `AdminPostEdit.vue` | admin |
| `/admin/posts/:slug/edit` | `AdminPostEdit.vue` | admin |
| `/admin/projects` | `AdminProjects.vue` | admin |
| `/admin/users` | `AdminUsers.vue` | admin |
| `/admin/comments` | `AdminComments.vue` | admin |
| `/admin/photos` | `AdminPhotos.vue` | admin |
| `/admin/chat` | `AdminChat.vue` | admin |

`/admin/login` 已重定向到首页，登录通过导航栏弹窗完成。

### 路由守卫注意点

守卫（`beforeEach` / `afterEach`）在 `router/index.ts` **模块级**注册，不在任何组件 `setup()` 内注册，避免 HMR 热更新时重复累积。守卫同时导出 `isPageLoading: Ref<boolean>` 供 `App.vue` 的 `<LoadingOverlay>` 使用。

## 5. API 概览

前端统一通过 `src/api/client.ts` 的 `api` 对象发请求，自动附带 `qi_token` JWT。所有页面/组件不直接调用 `fetch`。

### 用户

- `POST /api/users/register`
- `POST /api/users/login`
- `GET /api/users/me`
- `PATCH /api/users/me`
- `PATCH /api/users/password`

### 文章

- `GET /api/posts?page=1&limit=10&tag=Vue`
- `GET /api/posts/{slug}`
- `GET /api/posts/{slug}/adjacent`
- `POST /api/posts`，admin
- `PATCH /api/posts/{slug}`，admin
- `DELETE /api/posts/{slug}`，admin

### 项目

- `GET /api/projects`
- `GET /api/projects?category=前端`
- `POST /api/projects`，admin
- `PATCH /api/projects/{id}`，admin
- `DELETE /api/projects/{id}`，admin

### 评论

- `GET /api/comments/{post_slug}`
- `POST /api/comments/{post_slug}`，登录用户
- `DELETE /api/comments/{comment_id}`，本人或 admin
- `DELETE /api/comments/admin/{comment_id}`，admin

### 相册

- `GET /api/photos`
- `POST /api/photos`，admin（multipart/form-data）
- `PATCH /api/photos/{id}`，admin
- `DELETE /api/photos/{id}`，admin

### AI 对话

- `POST /api/chat/message`，登录用户，SSE 流式响应
- `GET /api/chat/history`，登录用户
- `DELETE /api/chat/history`，登录用户
- `POST /api/chat/tts`，登录用户，返回 `audio/mpeg` 二进制流（阿里云 NLS 合成）

### 后台统计

- `GET /api/admin/stats`，admin  
  返回字段：`post_count`, `pub_count`, `view_total`, `comment_count`, `user_count`, `monthly_posts`, `monthly_comments`, `top_posts`, `chat_msg_count`, `chat_user_count`, `monthly_chats`, `active_chatters`

### 许愿池

- `POST /api/wishes`，登录用户，新增许愿
- `GET /api/wishes`，获取许愿列表（公开）
- `DELETE /api/wishes/{id}`，本人或 admin

### 后台管理

- `GET /api/admin/users`，admin
- `PATCH /api/admin/users/{id}`，admin
- `DELETE /api/admin/users/{id}`，admin
- `GET /api/admin/comments?user_id=`，admin
- `GET /api/admin/chat`，admin（列出有聊天记录的用户及统计）
- `GET /api/admin/chat/{user_id}`，admin
- `DELETE /api/admin/chat/{user_id}`，admin
- `GET /api/admin/wishes`，admin
- `DELETE /api/admin/wishes/{id}`，admin

## 6. 环境变量

后端 `.env`（不入 git）必需字段：

| 变量 | 说明 |
|---|---|
| `DATABASE_URL` | asyncpg 连接串 |
| `SECRET_KEY` | JWT 签名密钥 |
| `ALGORITHM` | 固定 `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分钟） |
| `ADMIN_USERNAME` | 管理员用户名 |
| `ADMIN_PASSWORD_HASH` | bcrypt 哈希，启动时自动同步到数据库 |
| `ADMIN_EMAIL` | 管理员邮箱 |
| `CORS_ORIGINS` | 逗号分隔的允许来源 |
| `DEEPSEEK_API_KEY` | DeepSeek AI 密钥 |
| `ALIYUN_NLS_APPKEY` | 阿里云 NLS 语音合成 AppKey |
| `ALIYUN_ACCESS_KEY_ID` | 阿里云 RAM AccessKey ID |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云 RAM AccessKey Secret |
| `PHOTOS_DIR` | 图片存储绝对路径 |

## 7. TTS 架构说明

**不使用** Web Speech API 或 edge-tts，两者在国内均不可靠。

当前方案：
1. 后端 `routers/chat.py` 持有 NLS Token 缓存（`_nls_cache`），通过 HMAC-SHA1 签名动态获取或直接读取 `ALIYUN_NLS_TOKEN` 静态变量。
2. `POST /api/chat/tts` 接收 `{ text, voice? }` → 调用 `nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts` → 将 mp3 二进制直接返回给前端。
3. 前端 `ChatWidget.vue` 的 `speakText()` 用 `fetch` 拿到 blob，`URL.createObjectURL` 后传给 `new Audio()` 播放。
4. 支持中途 `stopSpeech()`：`pause()` 当前 Audio 实例，释放 ObjectURL。

## 8. 资源规范

### assetUrl() 工具函数

位置：`frontend/src/utils/assets.ts`

用途：处理 Vite `base` 前缀（开发 `/`，生产 `/blog/`），确保 `public/` 下资源在生产环境路径正确。

```ts
import { assetUrl } from '@/utils/assets'
// 开发：/tiles/qi-tile-write.png
// 生产：/blog/tiles/qi-tile-write.png
assetUrl('/tiles/qi-tile-write.png')
```

**重要：** `public/` 下的资源（tiles、animations、avatars）在模板或 JS 中引用时，必须通过 `assetUrl()` 包裹，否则生产环境路径会缺失 `/blog/` 前缀导致 404。

### 2048 Tile 图片资源

位置：`frontend/public/tiles/`

当前 11 个游戏值对应的 tile 文件：

| 值 | 文件名 |
|---|---|
| 2 | `qi-tile-write.png` |
| 4 | `qi-tile-code.png` |
| 8 | `qi-tile-relax.png` |
| 16 | `qi-tile-photo.png` |
| 32 | `qi-tile-think.png` |
| 64 | `qi-tile-bath.png` |
| 128 | `qi-tile-read.png` |
| 256 | `qi-tile-cheer.png` |
| 512 | `qi-tile-snack.png` |
| 1024 | `qi-tile-trophy.png` |
| 2048 | `qi-tile-wind.png` |

额外备用（未用于游戏）：`qi-tile-sleep`, `qi-tile-yawn`, `qi-tile-music`, `qi-tile-garden`, `qi-tile-star`, `qi-tile-bike`, `qi-tile-rain`

源图：`grid1.png`（九宫格 1）、`grid2.png`（九宫格 2），裁剪脚本在 `scripts/tile-crop/`，`GAP=6 INSET=20`，输出 256×256 PNG。

### 水豚动画

位置：`frontend/public/animations/`

当前组件通过站点根路径访问，例如：

```text
/animations/qi_wave_medium.webp
/animations/qi_type_small_transp.gif
/animations/qi_wind_medium.webp   ← LoadingOverlay 使用
```

`QiMascot.vue` 支持：

- state: `wave | type | think | wind | singing | wake`
- size: `small | medium | large`
- `autoSwitch`: 跟随滚动进度切换状态

`LoadingOverlay.vue`：
- 页面路由跳转时显示，`App.vue` 通过 `isPageLoading` ref 控制
- 使用 `qi_wind_medium.webp`，浮动动效
- Vue Transition `name="qi-loading"` 淡入/淡出

注意：

- `singing` 当前映射到 `wave` 资源。
- 不要把暗色主题选择器写成 `:global([data-theme="dark"]) .xxx`，在 Vue scoped CSS 下应写成 `:global([data-theme="dark"] .xxx)`。

### 固定头像库

位置：`frontend/public/avatars/`

当前只允许五个头像：

```text
qi-avatar-coding.png
qi-avatar-wake.png
qi-avatar-wind.png
qi-avatar-wave.png
qi-avatar-think.png
```

用户资料页保存的是站内路径：

```text
/avatars/qi-avatar-coding.png
```

不要恢复自由头像 URL 输入，避免外链失效、混合内容和不可控资源。

## 9. 设计系统

全局 token 在 `frontend/src/styles/tokens.css`。

主要变量：

```css
--qi-primary: #FF8C5A;
--qi-accent: #FFD166;
--qi-soft: #F4A0A0;
--qi-wind: #A8D8C0;
--qi-bg: #FFF8F0;
--qi-bg-card: #FFF0E0;
--qi-bg-muted: #FFF4E8;
--qi-ink: #3A2A1A;
--qi-ink-muted: #8A7060;
--qi-ink-light: #C4A898;
--qi-border: rgba(255, 140, 90, 0.15);
--qi-shadow: rgba(58, 42, 26, 0.08);
```

暗色主题使用 `[data-theme="dark"]` 覆盖变量，不要在组件里硬编码大面积暗色。

视觉规则：

- 公开页：留白充分、暖色、轻动画。
- 后台页：更克制，避免装饰过多，强调表格、表单和操作效率。
- 卡片圆角一般不超过 16px；工具类小控件 8-12px；药丸按钮可用 999px。
- 不要用一整页同一色相堆叠，必要时用边框、透明层和浅背景分层。
- 禁止让固定元素或图片 transform 造成横向溢出。

## 10. 前端代码规范

### Vue 与 TypeScript

- 所有 Vue 文件使用 `<script setup lang="ts">`。
- props、emit、表单对象、API payload 必须有明确类型。
- `computed` 用于派生状态；不要在模板里写复杂表达式。
- `watch` 只处理同步外部状态到本地表单、节流副作用或必要异步更新。
- 避免 `any`；适配后端原始数据时可局部使用，并尽快转成前端类型。
- 不允许为了通过编译关闭 `strict`、`noUnusedLocals`、`noUnusedParameters`。

### 组件拆分

- 可复用 UI 放 `src/components/`。
- 页面级业务放 `src/views/`。
- 跨页面状态放 `src/stores/`。
- 纯组合逻辑放 `src/composables/`。
- API 请求只放 `src/api/`，统一通过 `api` client 对象，不直接 `fetch`。

### 样式

- 优先使用 `var(--qi-*)` 和 `var(--navbar-*)`。
- 组件局部样式使用 `<style scoped>`。
- 全局 reset、动画 keyframes、主题变量只放 `tokens.css`。
- 使用 `box-sizing: border-box` 的前提设计尺寸，避免 `100vw` 造成横向滚动。
- 页面级固定高度必须确认移动端有 fallback，避免内容被裁。
- 文本必须在移动端可换行，不允许按钮或卡片文字溢出。

### 资源引用

- `public` 下资源用站点根路径：`/avatars/...`、`/animations/...`。
- `src/assets` 下资源用于构建打包导入。
- 用户可选择的头像必须来自白名单。

### 表单

- 表单字段命名和后端 API payload 分开处理：
  - 前端表单可用 camelCase。
  - 发给后端时转换成 snake_case。
- 保存失败必须展示后端错误信息或明确 fallback 文案。
- loading 状态必须禁用提交按钮。

## 11. 后端代码规范

- router 按领域放在 `backend/routers/`。
- 公开接口和 admin 接口明确依赖：
  - 登录用户：`Depends(get_current_user)`
  - 管理员：`Depends(get_current_admin)`
- 请求/响应模型放 `models.py`，不要直接返回不受控 dict，统计类接口除外。
- 数据库访问使用 `AsyncSession`。
- 修改数据库对象后必须 `session.add()`、`commit()`，需要返回最新数据时 `refresh()`。
- 错误响应使用 `HTTPException`，状态码要语义清晰。
- 不要把真实数据库连接、JWT secret、AccessKey 写入文档或提交到仓库。
- 外部 HTTP 请求（DeepSeek、阿里云 NLS）使用 `httpx.AsyncClient`。

## 12. 常用命令

### 前端

```powershell
cd D:\代码汇中\个人作品集博客\frontend
npm install
npm run dev
npm.cmd run build
```

PowerShell 执行 `npx` 可能被策略拦截，优先用：

```powershell
npm.cmd exec vite build
```

### 后端

```powershell
cd D:\代码汇中\个人作品集博客\backend
uvicorn main:app --reload --port 8000
```

如使用 conda，先激活项目环境。

## 13. 验证清单

每次改动完成至少检查：

- `npm.cmd run build`
- 受影响页面在亮色/暗色主题下是否正常。
- 是否出现横向滚动条。
- 导航栏、固定右下角水豚、返回顶部按钮是否遮挡核心内容。
- 登录态相关页面是否处理未登录、普通用户、admin 三种情况。
- API payload 字段是否与后端模型一致。

前端视觉改动需要额外检查：

- 1280px 桌面。
- 768px 附近断点。
- 390px 移动宽度。
- 暗色模式。

## 14. 已知注意点

- 右下角固定水豚属于装饰元素，不能影响布局宽度。
- 个人资料页桌面端当前按单屏优化，移动端保留滚动。
- build 可能提示大 chunk 警告，当前不阻塞构建；如后续优化，可考虑后台图表和文章详情拆 chunk。
- 文档和源码统一保存为 UTF-8，避免中文乱码。
- 路由守卫只在 `router/index.ts` 模块级注册，不在组件 `setup()` 内重复注册（HMR 会重复累积）。
- TTS 不使用 Web Speech API 或 edge-tts，必须通过 `/api/chat/tts` 后端代理阿里云 NLS。
