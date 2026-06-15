# 起风了个人作品集博客 - 当前进度

> 最后整理：2026-06-15
> 本文记录当前仓库实际状态、验证命令、已完成能力和后续优化项。

## 1. 项目概况

| 项目 | 当前状态 |
|---|---|
| 项目名 | 起风了个人作品集博客 |
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router + UnoCSS |
| 后端 | FastAPI + SQLModel + PostgreSQL |
| 公开站点 | 已实现 |
| 登录与用户资料 | 已实现 |
| 评论系统 | 已实现 |
| 博主管理后台 | 已实现，含 AI 对话管理 |
| AI 对话 + TTS | 已实现（阿里云 NLS 语音合成） |
| 暗色模式 | 已实现并修复导航/横向溢出问题 |
| 固定头像选择 | 已实现，5 个站内头像 |
| 页面加载动画 | 已实现，水豚 LoadingOverlay |
| 当前构建状态 | `npm.cmd run build` 通过 |

## 2. 启动方式

### 前端开发服务

```powershell
cd D:\代码汇中\个人作品集博客\frontend
npm install
npm run dev
```

默认访问：

```text
http://localhost:5173
```

### 前端完整构建

```powershell
cd D:\代码汇中\个人作品集博客\frontend
npm.cmd run build
```

当前构建通过。Vite 会提示部分 chunk 超过 500kB，这是体积警告，不是编译错误。

### 后端开发服务

```powershell
cd D:\代码汇中\个人作品集博客\backend
uvicorn main:app --reload --port 8000
```

默认 API：

```text
http://localhost:8000
http://localhost:8000/docs
```

## 3. 当前功能状态

### 公开前台

| 功能 | 状态 | 说明 |
|---|---|---|
| 首页 | 完成 | Hero、项目预览、文章预览、水豚动效 |
| 关于页 | 完成 | 个人介绍、技能/经历展示 |
| 项目页 | 完成 | 项目列表和分类筛选 |
| 博客列表 | 完成 | 搜索、标签过滤、分页 |
| 文章详情 | 完成 | Markdown 渲染、代码高亮、阅读进度、目录、上一篇/下一篇 |
| 评论区 | 完成 | 登录用户评论、删除权限控制 |
| 404 | 完成 | 自定义页面 |
| 导航栏 | 完成 | 登录入口、用户菜单、暗色模式切换 |
| 右下角水豚 | 完成 | 跟随滚动自动切换状态 |
| 页面跳转加载动画 | 完成 | 200ms 延迟触发，防抖设计，水豚 + 浮动动效 |

### 用户系统

| 功能 | 状态 | 说明 |
|---|---|---|
| 注册 | 完成 | `/api/users/register` |
| 登录 | 完成 | JWT 保存到 `qi_token` |
| 当前用户 | 完成 | `/api/users/me` |
| 资料编辑 | 完成 | 用户名、简介、固定头像 |
| 头像选择 | 完成 | 仅允许 5 个 `/avatars/...png` |
| 修改密码 | 完成 | `/api/users/password` |
| 路由守卫 | 完成 | `/profile` 需登录，`/admin` 需 admin，守卫在 router 模块级注册 |

### AI 对话

| 功能 | 状态 | 说明 |
|---|---|---|
| 聊天 Widget | 完成 | 右下角展开/收起，流式输出 |
| DeepSeek 接入 | 完成 | 流式 SSE |
| TTS 语音播放 | 完成 | 阿里云 NLS，mp3 blob + HTML Audio，全浏览器兼容 |
| 聊天历史 | 完成 | 每用户持久化到 PostgreSQL |

### 后台管理

| 功能 | 状态 | 说明 |
|---|---|---|
| 后台布局 | 完成 | 侧边栏 + 内容区 |
| 仪表盘 | 完成 | 文章/评论/用户/阅读/AI 对话六维统计，含雷达图、折线图、进度条排行 |
| 文章管理 | 完成 | 列表、删除 |
| 文章编辑 | 完成 | 新建/编辑，Markdown 编辑器 |
| 项目管理 | 完成 | 新建、编辑、删除 |
| 用户管理 | 完成 | 列表、编辑角色/信息、删除 |
| 评论管理 | 完成 | 列表、筛选用户、删除 |
| 相册管理 | 完成 | 上传、排序、删除 |
| AI 对话管理 | 完成 | 查看各用户聊天记录、清空 |
| 管理员接口保护 | 完成 | `get_current_admin` |

### 后端 API

| 模块 | 状态 |
|---|---|
| posts | 完成 |
| projects | 完成 |
| users | 完成 |
| comments | 完成 |
| photos | 完成 |
| chat（AI 对话 + TTS） | 完成 |
| admin stats（含 AI 对话统计） | 完成 |
| admin users/comments/chat | 完成 |
| auth/JWT | 完成 |
| CORS | 开发/生产环境已配置 |

## 4. 重要资源

### 动画资源

位置：

```text
frontend/public/animations/
```

主要文件：

- `qi_wave_*`
- `qi_type_*`
- `qi_think_*`
- `qi_wind_*`
- `qi_wake_*`
- `qi_small.*`

组件入口：

```text
frontend/src/components/QiMascot.vue
frontend/src/components/LoadingOverlay.vue   ← 页面跳转加载动画
```

### 头像资源

位置：

```text
frontend/public/avatars/
```

文件：

```text
qi-avatar-coding.png
qi-avatar-wake.png
qi-avatar-wind.png
qi-avatar-wave.png
qi-avatar-think.png
```

使用页面：

```text
frontend/src/views/ProfileView.vue
```

保存值示例：

```text
/avatars/qi-avatar-coding.png
```

## 5. 最近已修复问题

### TTS 方案替换（edge-tts → 阿里云 NLS）

- edge-tts 在国内被 Microsoft CDN 封锁，返回 403。
- Web Speech API 不可靠，依赖浏览器语音库，质量参差。
- 当前方案：后端通过 HMAC-SHA1 签名获取 NLS Token，调用 `nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts` 返回 mp3 音频流，前端用 `new Audio(blobUrl)` 播放。

### 页面加载动画（LoadingOverlay）

- 新增 `LoadingOverlay.vue`，页面路由跳转时显示全屏水豚浮动动画。
- 路由守卫在 `router/index.ts` 模块级注册（不在组件 `setup()` 内），避免 HMR 热更新时重复累积。

### 管理后台仪表盘升级

- 后端 `/api/admin/stats` 新增 AI 对话统计字段：`chat_msg_count`、`chat_user_count`、`monthly_chats`、`active_chatters`。
- 前端 AdminDashboard 重新设计：统计卡片 5→6 张、新增雷达图（六维数据对比）、AI 对话折线图、HTML 进度条 Top5、活跃聊天用户面板。

### 代码质量修复（项目审计）

- `backend/database.py`：管理员密码同步逻辑修复——原为死代码（条件永远为 False），改为哈希比对后按需更新。
- `frontend/src/api/users.ts`：移除冗余 `const BASE`，`login()` 和 `me()` 改用统一的 `api` helper。
- `frontend/src/stores/user.ts`：`usersApi.me()` 去掉多余 token 参数。
- `frontend/src/types/index.ts`：`Project` 接口补充 `projectId?: string` 字段。
- `frontend/src/api/projects.ts`：`adapt()` 映射 `raw.project_id → projectId`。

### 暗色模式导航和滚动条

- `QiMascot.vue` scoped CSS 中暗色选择器已修正为 `:global([data-theme="dark"] .qi-mascot)`。

## 6. 当前代码规范摘要

### 前端

- Vue 文件统一使用 `<script setup lang="ts">`。
- 不关闭 TypeScript 严格检查。
- API 请求集中在 `src/api/`，统一通过 `api` client 发送（自动附 token）。
- 页面使用 `src/views/`，通用 UI 使用 `src/components/`。
- 颜色和主题使用 `tokens.css` 中的 CSS 变量。
- 暗色模式只覆盖变量或精确组件选择器。
- 固定定位元素不能造成横向溢出。
- 头像选择只能使用 `public/avatars` 白名单。
- 表单保存要有 loading、错误提示和成功反馈。
- 路由守卫只在 `router/index.ts` 模块级注册，不在组件内重复注册。

### 后端

- 按领域拆 router。
- 需要登录的接口使用 `get_current_user`。
- 需要管理员的接口使用 `get_current_admin`。
- 请求/响应模型放在 `models.py`。
- 数据库操作使用异步 session。
- 不在代码或文档中暴露真实密钥。

## 7. 后续优化项

### 高优先级

| 项目 | 说明 |
|---|---|
| 生产部署验证 | 首次升级部署后逐项核查 DEPLOY.md 快速验证清单 |
| 阿里云 NLS 配额确认 | 确认 NLS 免费额度是否满足生产用量，必要时开通付费套餐 |

### 中优先级

| 项目 | 说明 |
|---|---|
| 大 chunk 优化 | AdminDashboard、PostView 体积较大，可拆分图表和 Markdown 相关依赖 |
| 图片资源压缩 | 头像 PNG 体积较大，可转 WebP 或生成缩略图 |
| 关于页内容完善 | 替换占位介绍为正式内容 |
| 项目封面上传 | 当前项目封面/文章封面仍偏 URL 模式，可后续接入上传 |

### 低优先级

| 项目 | 说明 |
|---|---|
| 评论通知 | 新评论提醒或邮件通知 |
| SEO 元信息 | 为文章详情和首页补充动态 title/description |

## 8. 验收清单

交付前建议按顺序检查：

1. `npm.cmd run build`
2. 首页、博客页、文章详情、项目页、关于页、资料页、后台页能打开。
3. 页面跳转时出现水豚加载动画（慢网络下，200ms 延迟后显示）。
4. 亮色/暗色模式切换正常。
5. 桌面端无横向滚动条。
6. `/profile` 未登录会跳回首页并要求登录。
7. 普通用户不能访问 `/admin`。
8. admin 可进入后台并新增/编辑文章项目。
9. 后台仪表盘六个统计卡片、图表、活跃用户面板正常显示。
10. AI 对话 TTS 可正常播放（阿里云 NLS）。
11. 头像只能从 5 个固定头像中选择。
12. 评论新增和删除权限符合预期。

## 9. 不要做的事

- 不要把 `node_modules`、`dist`、`.env`、`__pycache__` 纳入版本管理。
- 不要在文档中写真实密码、JWT secret、数据库明文连接串、AccessKey 或服务器私密信息。
- 不要恢复自由头像 URL 输入。
- 不要为了消除滚动条全局禁用 `body` 滚动；应在具体页面内解决布局。
- 不要用硬编码颜色绕过 `tokens.css`，除非是非常局部且有明确原因的状态色。
- 不要在组件 `setup()` 里注册路由守卫，统一在 `router/index.ts` 模块级注册。
