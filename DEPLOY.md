# 起风了博客 — 部署文档

> 目标地址：`https://www.optlab.space/blog/`  
> 服务器：`47.116.111.170`（阿里云）  
> 运行环境：Python 3.9（conda `qi-blog`）、PostgreSQL（云数据库 55432 端口）、nginx

---

## 目录结构（服务器端）

```
/var/www/qi-blog/
├── dist/          # 前端打包产物（每次更新覆盖）
├── photos/        # 用户上传的图片（持久化，不覆盖）
└── exes/          # 程序压缩包（只上传一次，不随版本更新）
    ├── 波动光学可视化平台.zip
    └── 光学虚拟实验平台.zip

/opt/qi-blog/
└── repo/          # git clone 的完整仓库（git pull 更新）
    └── backend/   # 后端代码，systemd 服务指向此目录
```

---

## 一、首次部署

### 1. 服务器准备

```bash
# 创建目录
mkdir -p /var/www/qi-blog/{dist,photos,exes}
mkdir -p /opt/qi-blog

# 克隆后端代码
cd /opt/qi-blog
git clone <你的仓库地址> .

# 安装后端依赖（使用 conda qi-blog 环境）
conda activate qi-blog
pip install -r /opt/qi-blog/backend/requirements.txt
```

### 2. 后端 `.env` 配置

```bash
cp /opt/qi-blog/backend/.env.example /opt/qi-blog/backend/.env
```

编辑 `/opt/qi-blog/backend/.env`，填入：

```env
DATABASE_URL=postgresql+asyncpg://postgres:<密码>@47.116.111.170:55432/qiblog
SECRET_KEY=<随机长字符串，生产必须修改>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

ADMIN_USERNAME=qi
ADMIN_PASSWORD_HASH=<用下方命令生成>
ADMIN_EMAIL=qi@example.com

CORS_ORIGINS=https://www.optlab.space,https://optlab.space

DEEPSEEK_API_KEY=<你的 DeepSeek Key>

# 阿里云 NLS 文字转语音（AI 对话 TTS 功能必需）
ALIYUN_NLS_APPKEY=<NLS 控制台的 AppKey>
ALIYUN_ACCESS_KEY_ID=<AccessKey ID>
ALIYUN_ACCESS_KEY_SECRET=<AccessKey Secret>

# 图片存储目录（必须与 nginx alias 一致）
PHOTOS_DIR=/var/www/qi-blog/photos
```

生成密码哈希：
```bash
conda run -n qi-blog python -c \
  "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('你的密码'))"
```

### 3. 创建 systemd 服务

```bash
cat > /etc/systemd/system/qi-blog.service << 'EOF'
[Unit]
Description=起风了博客后端 (FastAPI)
After=network.target

[Service]
User=root
WorkingDirectory=/opt/qi-blog/backend
EnvironmentFile=/opt/qi-blog/backend/.env
ExecStart=/root/anaconda3/envs/qi-blog/bin/uvicorn main:app \
          --host 127.0.0.1 --port 8765 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qi-blog
systemctl start qi-blog

# 确认运行
systemctl status qi-blog
curl http://127.0.0.1:8765/
```

> **端口选 8765** 避免与服务器上其他服务冲突。

### 4. 上传 exe 压缩包（仅一次）

```bash
# 在本机执行（Windows 用 WinSCP 或以下命令）
scp "frontend/public/exes/波动光学可视化平台.zip" root@47.116.111.170:/var/www/qi-blog/exes/
scp "frontend/public/exes/光学虚拟实验平台.zip"   root@47.116.111.170:/var/www/qi-blog/exes/
```

这两个文件**不随版本更新**，上传一次即可。

### 5. 配置 nginx

在现有 `optlab.space` 的 nginx 配置文件中（通常在 `/etc/nginx/sites-available/optlab.space` 或 `/etc/nginx/conf.d/optlab.space.conf`）追加以下 location 块：

```nginx
# ── 起风了博客 ──────────────────────────────────────────────────

# 前端 SPA（/blog/ 子路径）
location /blog/ {
    alias /var/www/qi-blog/dist/;
    try_files $uri $uri/ @qi_blog_spa;
    expires 7d;
    add_header Cache-Control "public, immutable";
}
location = /blog/index.html {
    alias /var/www/qi-blog/dist/index.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
location @qi_blog_spa {
    rewrite .* /blog/index.html last;
}

# 后端 API
location /api/ {
    proxy_pass         http://127.0.0.1:8765;
    proxy_set_header   Host $host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
    # 文件上传允许最大 15 MB
    client_max_body_size 15m;
    # AI 流式响应不缓冲
    proxy_buffering    off;
    proxy_cache        off;
}

# 图片（由后端写入，nginx 直接静态服务）
location /photos/ {
    alias /var/www/qi-blog/photos/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# 程序下载包
location /exes/ {
    alias /var/www/qi-blog/exes/;
    add_header Content-Disposition 'attachment';
}
```

```bash
nginx -t && systemctl reload nginx
```

### 6. 首次前端部署

在**本机**执行：

```bash
cd frontend
npm run build         # 自动读取 .env.production，base=/blog/，VITE_API_BASE=''
```

将 `frontend/dist/` 上传到服务器（**不包含 exes 目录，exes 已单独上传**）：

```bash
rsync -avz --delete \
  frontend/dist/ \
  root@47.116.111.170:/var/www/qi-blog/dist/
```

访问 `https://www.optlab.space/blog/` 验证。

---

## 二、日常更新

### 前端更新

```bash
# 本机
cd frontend
npm run build
rsync -avz --delete frontend/dist/ root@47.116.111.170:/var/www/qi-blog/dist/
```

无需重启任何服务，nginx 直接服务静态文件。

### 后端更新

```bash
# 本机：先推送到 GitHub
git push origin main

# 服务器上执行
cd /opt/qi-blog/repo && git pull && systemctl restart qi-blog && systemctl status qi-blog
```

> `.env` 和 `.venv` 不在 git 中，`git pull` 不会覆盖，无需担心。

### 新增图片/资产

图片通过博客后台管理页面（`/blog/admin/photos`）上传，后端自动写入 `/var/www/qi-blog/photos/`，无需手动操作。

---

## 三、关于 exe 大文件的处理说明

`exes/` 里的两个压缩包（各几十 MB）处理策略：

| 情况 | 操作 |
|------|------|
| 首次部署 | 手动 scp 上传到 `/var/www/qi-blog/exes/` |
| 前端更新（`rsync dist/`） | **不涉及**，exes 不在 dist 内 |
| 新增/替换程序包 | 手动 scp 上传对应文件，同步更新 DB 的 `url` 字段 |

`.gitignore` 中应排除 `frontend/public/exes/*.zip`，避免大文件进入仓库：

```gitignore
frontend/public/exes/*.zip
```

---

## 四、快速验证清单

部署完成后逐项检查：

- [ ] `https://www.optlab.space/blog/` 首页正常加载，页面跳转时出现水豚加载动画
- [ ] `https://www.optlab.space/blog/projects` 显示项目列表（从数据库加载）
- [ ] `https://www.optlab.space/blog/photos` 显示相册图片
- [ ] `https://www.optlab.space/api/` 返回 `{"message":"起风了 API · 正在运行"}`
- [ ] `/blog/admin` 用管理员账号可以登录
- [ ] 后台仪表盘显示文章、评论、用户、AI 对话统计
- [ ] 后台图片上传测试：上传一张图片，相册页面可见
- [ ] 下载按钮：点击 QT 项目卡片的"⬇ 下载程序"，浏览器触发下载
- [ ] 水豚祁 AI 对话正常响应（流式输出）
- [ ] AI 对话 TTS：点击播放按钮，能听到阿里云 NLS 合成语音
- [ ] 后台 `/admin/chat` 能查看用户聊天记录并支持清空

---

## 五、常用命令速查

```bash
# 查看后端日志
journalctl -u qi-blog -f

# 重启后端
systemctl restart qi-blog

# 查看 nginx 错误日志
tail -f /var/log/nginx/error.log

# 手动测试后端 API
curl http://127.0.0.1:8765/api/projects

# 检查端口是否监听
ss -tlnp | grep 8765
```
