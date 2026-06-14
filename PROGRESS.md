# 起风了个人作品集博客 - 当前进度

> 最后整理：2026-06-13
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
| 博主管理后台 | 已实现 |
| 暗色模式 | 已实现并修复导航/横向溢出问题 |
| 固定头像选择 | 已实现，5 个站内头像 |
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

### 用户系统

| 功能 | 状态 | 说明 |
|---|---|---|
| 注册 | 完成 | `/api/users/register` |
| 登录 | 完成 | JWT 保存到 `qi_token` |
| 当前用户 | 完成 | `/api/users/me` |
| 资料编辑 | 完成 | 用户名、简介、固定头像 |
| 头像选择 | 完成 | 仅允许 5 个 `/avatars/...png` |
| 修改密码 | 完成 | `/api/users/password` |
| 路由守卫 | 完成 | `/profile` 需登录，`/admin` 需 admin |

### 后台管理

| 功能 | 状态 | 说明 |
|---|---|---|
| 后台布局 | 完成 | 侧边栏 + 内容区 |
| 仪表盘 | 完成 | 文章、评论、用户、阅读数据统计 |
| 文章管理 | 完成 | 列表、删除 |
| 文章编辑 | 完成 | 新建/编辑，Markdown 编辑器 |
| 项目管理 | 完成 | 新建、编辑、删除 |
| 管理员接口保护 | 完成 | `get_current_admin` |

### 后端 API

| 模块 | 状态 |
|---|---|
| posts | 完成 |
| projects | 完成 |
| users | 完成 |
| comments | 完成 |
| admin stats | 完成 |
| auth/JWT | 完成 |
| CORS | 开发环境已配置 |

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

### 暗色模式导航和滚动条

问题：

- 暗色模式下导航栏看起来被顶出视口。
- 页面右侧出现异常滚动/白边。

原因：

- `QiMascot.vue` scoped CSS 中暗色选择器写法不正确，`transform: scale(1.065)` 被错误应用到 `html[data-theme="dark"]`。

修复：

- 将选择器改为完整全局选择器：

```css
:global([data-theme="dark"] .qi-mascot)
:global([data-theme="dark"] .qi-mascot-img)
```

### TypeScript 构建错误

已修复：

- 新增 `src/vite-env.d.ts`。
- 清理未使用 import/变量。
- 新建文章 payload 补齐 `published`。
- 项目表单 `status` 显式声明为 `Project['status']`。

### 个人资料页

已完成：

- 重新设计布局。
- 移除自由头像 URL。
- 固定 5 个头像选择。
- 桌面端压缩成单屏布局，避免页面滚动条。
- 移动端保留滚动，避免内容被裁。

## 6. 当前代码规范摘要

### 前端

- Vue 文件统一使用 `<script setup lang="ts">`。
- 不关闭 TypeScript 严格检查。
- API 请求集中在 `src/api/`。
- 页面使用 `src/views/`，通用 UI 使用 `src/components/`。
- 颜色和主题使用 `tokens.css` 中的 CSS 变量。
- 暗色模式只覆盖变量或精确组件选择器。
- 固定定位元素不能造成横向溢出。
- 头像选择只能使用 `public/avatars` 白名单。
- 表单保存要有 loading、错误提示和成功反馈。

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
| 检查后端中文乱码 | 部分 Python 文件在终端输出中显示乱码，需要确认文件编码是否为 UTF-8 |
| 生产环境配置 | CORS、数据库连接、JWT secret 应拆到生产环境变量 |
| 后端接口回归 | 对 posts/projects/users/comments/admin 做一次完整接口测试 |

### 中优先级

| 项目 | 说明 |
|---|---|
| 大 chunk 优化 | `AdminDashboard`、`PostView` 体积较大，可拆分图表和 Markdown 相关依赖 |
| 图片资源压缩 | 头像 PNG 体积较大，可转 WebP 或生成缩略图 |
| 关于页内容完善 | 替换占位介绍为正式内容 |
| 项目封面上传 | 当前项目封面/文章封面仍偏 URL 模式，可后续接入上传 |

### 低优先级

| 项目 | 说明 |
|---|---|
| 评论通知 | 新评论提醒或邮件通知 |
| 阅读数据报表 | 基于 `view_count` 和评论做更细后台分析 |
| SEO 元信息 | 为文章详情和首页补充动态 title/description |

## 8. 验收清单

交付前建议按顺序检查：

1. `npm.cmd run build`
2. 首页、博客页、文章详情、项目页、关于页、资料页、后台页能打开。
3. 亮色/暗色模式切换正常。
4. 桌面端无横向滚动条。
5. `/profile` 未登录会跳回首页并要求登录。
6. 普通用户不能访问 `/admin`。
7. admin 可进入后台并新增/编辑文章项目。
8. 头像只能从 5 个固定头像中选择。
9. 评论新增和删除权限符合预期。

## 9. 不要做的事

- 不要把 `node_modules`、`dist`、`.env`、`__pycache__` 纳入版本管理。
- 不要在文档中写真实密码、JWT secret、数据库明文连接串或服务器私密信息。
- 不要恢复自由头像 URL 输入。
- 不要为了消除滚动条全局禁用 `body` 滚动；应在具体页面内解决布局。
- 不要用硬编码颜色绕过 `tokens.css`，除非是非常局部且有明确原因的状态色。
