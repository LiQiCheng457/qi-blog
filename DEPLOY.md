# 起风了博客 — 部署文档

> 目标地址：`https://www.optlab.space/blog/`  
> 服务器：`47.116.111.170`（阿里云）  
> 运行环境：Python 3.10（`.venv`）、PostgreSQL（云数据库 55432 端口）、nginx  
> 仓库：`git@github.com:LiQiCheng457/qi-blog.git`

---

## 目录结构（服务器端）

```
/var/www/qi-blog/
├── dist/          # 前端打包产物（每次更新覆盖，排除 exes/photos）
├── photos/        # 用户上传的图片（持久化，不覆盖）
└── exes/          # 程序压缩包（通过后台管理或手动 scp 上传）
    ├── 波动光学可视化平台.zip
    └── 光学虚拟实验平台.zip

/opt/qi-blog/
└── repo/                  # git clone 的完整仓库
    └── backend/           # 后端工作目录
        ├── .venv/         # 虚拟环境（不入 git，服务器本地创建）
        └── .env           # 环境变量（不入 git，手动维护）
```

nginx 配置文件：`/opt/optical-lab-platform/deploy-local/nginx-site.conf`  
systemd 服务文件：`/etc/systemd/system/qi-blog.service`

---

## 一、首次部署

### 1. 创建目录

```bash
mkdir -p /var/www/qi-blog/{dist,photos,exes}
mkdir -p /opt/qi-blog
```

### 2. 配置 GitHub Deploy Key

```bash
# 生成 deploy key
ssh-keygen -t ed25519 -C 'qi-blog-deploy' -f /root/.ssh/qi-blog-deploy -N ''
cat /root/.ssh/qi-blog-deploy.pub   # 复制公钥

# 配置 SSH 使用该 key 访问 GitHub
cat >> /root/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile /root/.ssh/qi-blog-deploy
    StrictHostKeyChecking no
EOF
```

将公钥加到 GitHub：仓库 → Settings → Deploy keys → Add deploy key（只读即可）。

验证：
```bash
ssh -T git@github.com
# 应显示：Hi LiQiCheng457/qi-blog! You've successfully authenticated...
```

### 3. 克隆仓库

```bash
cd /opt/qi-blog
git clone git@github.com:LiQiCheng457/qi-blog.git repo
```

### 4. 创建虚拟环境并安装依赖

```bash
cd /opt/qi-blog/repo/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> `requirements.txt` 锁定了 `cryptography==39.0.2`，与 `python-jose 3.3.0` 兼容。
> 不要升级 cryptography，否则 JWT 签发会报错。

### 5. 配置 `.env`

将本机 `backend/.env` 直接 scp 到服务器：

```bash
scp backend/.env root@47.116.111.170:/opt/qi-blog/repo/backend/.env
```

`.env` 完整字段说明：

```env
DATABASE_URL=postgresql+asyncpg://postgres:<密码>@47.116.111.170:55432/qiblog

SECRET_KEY=<随机长字符串，生产必须修改>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

ADMIN_USERNAME=qi
ADMIN_PASSWORD_HASH=<用下方命令生成>

# 生产跨域白名单
CORS_ORIGINS=https://www.optlab.space,https://optlab.space

# DeepSeek AI 聊天
DEEPSEEK_API_KEY=<你的 DeepSeek Key>

# 阿里云 NLS 文字转语音
ALIYUN_NLS_APPKEY=<NLS 控制台的 AppKey>
ALIYUN_ACCESS_KEY_ID=<AccessKey ID>
ALIYUN_ACCESS_KEY_SECRET=<AccessKey Secret>

# 文件存储目录（与 nginx alias 保持一致）
PHOTOS_DIR=/var/www/qi-blog/photos
EXES_DIR=/var/www/qi-blog/exes
```

生成密码哈希：
```bash
/opt/qi-blog/repo/backend/.venv/bin/python3 -c \
  "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('你的密码'))"
```

### 6. 创建 systemd 服务

```bash
cat > /etc/systemd/system/qi-blog.service << 'EOF'
[Unit]
Description=起风了博客后端 (FastAPI/uvicorn)
After=network.target

[Service]
User=root
WorkingDirectory=/opt/qi-blog/repo/backend
EnvironmentFile=/opt/qi-blog/repo/backend/.env
ExecStart=/opt/qi-blog/repo/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 1
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
curl http://127.0.0.1:8001/
```

> 端口使用 **8001**（8000 被光学平台占用，8765 被另一项目占用）。

### 7. 配置 nginx

在 `/opt/optical-lab-platform/deploy-local/nginx-site.conf` 的两个 server 块（HTTP 重定向块除外）内各追加以下 location：

```nginx
# ── 起风了博客 ──────────────────────────────────────────────────

location = /blog {
    return 301 /blog/;
}
location ^~ /blog/ {
    alias /var/www/qi-blog/dist/;
    index index.html;
    error_page 404 =200 /blog/index.html;
}
location = /blog/index.html {
    alias /var/www/qi-blog/dist/index.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}

# 博客 API（^~ 优先于静态资源正则，防止被拦截）
location ^~ /blog/api/ {
    proxy_pass http://127.0.0.1:8001/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300s;
    proxy_buffering off;
    proxy_cache off;
    client_max_body_size 15m;
}

# 用户上传图片
location ^~ /photos/ {
    alias /var/www/qi-blog/photos/;
    expires 30d;
}

# 动画资源（水豚）
location ^~ /animations/ {
    alias /var/www/qi-blog/dist/animations/;
    expires 30d;
}

# 程序下载包
location ^~ /exes/ {
    alias /var/www/qi-blog/exes/;
    add_header Content-Disposition attachment;
}
```

```bash
nginx -t && systemctl reload nginx
```

### 8. 首次前端部署

在**本机**执行（Windows 无 rsync，用 tar + scp）：

```powershell
cd frontend
npm run build

# 打包（排除大文件目录）
tar -czf C:/tmp/qi-blog-dist.tar.gz -C dist --exclude="./exes" --exclude="./photos" .

# 上传并解压
scp C:/tmp/qi-blog-dist.tar.gz root@47.116.111.170:/tmp/
ssh root@47.116.111.170 "tar -xzf /tmp/qi-blog-dist.tar.gz -C /var/www/qi-blog/dist/ && rm /tmp/qi-blog-dist.tar.gz"
```

访问 `https://www.optlab.space/blog/` 验证。

### 9. 上传 exe 压缩包

```bash
# 方式一：手动 scp（首次或替换文件时）
scp "前端/public/exes/波动光学可视化平台.zip" root@47.116.111.170:/var/www/qi-blog/exes/
scp "前端/public/exes/光学虚拟实验平台.zip"   root@47.116.111.170:/var/www/qi-blog/exes/

# 方式二：登录后台 /blog/admin/exes，通过页面上传
```

---

## 二、日常更新

### 前端更新

```powershell
# 本机
cd frontend
npm run build
tar -czf C:/tmp/qi-blog-dist.tar.gz -C dist --exclude="./exes" --exclude="./photos" .
scp C:/tmp/qi-blog-dist.tar.gz root@47.116.111.170:/tmp/
ssh root@47.116.111.170 "tar -xzf /tmp/qi-blog-dist.tar.gz -C /var/www/qi-blog/dist/ && rm /tmp/qi-blog-dist.tar.gz"
```

nginx 直接服务静态文件，无需重启任何服务。

### 后端更新

```powershell
# 1. 本机提交并推送
git push origin main

# 2. 服务器拉取并重启
ssh root@47.116.111.170 "cd /opt/qi-blog/repo && git pull && systemctl restart qi-blog && systemctl status qi-blog"
```

> `.env` 和 `.venv` 不在 git 中，`git pull` 不会覆盖。

### 更新 `.env` 配置

```powershell
# 修改本机 backend/.env 后直接 scp 覆盖
scp backend/.env root@47.116.111.170:/opt/qi-blog/repo/backend/.env
ssh root@47.116.111.170 "systemctl restart qi-blog"
```

### 新增图片

通过后台管理页面 `/blog/admin/photos` 上传，后端自动写入 `/var/www/qi-blog/photos/`，无需手动操作。

---

## 三、已知注意事项

| 事项 | 说明 |
|------|------|
| `cryptography` 版本 | 锁定在 `==39.0.2`，不可升级（python-jose 3.3.0 与 >=40 不兼容，JWT 会报错） |
| `.venv` 路径敏感 | 不要直接 cp 已有 `.venv`，内部 shebang 是绝对路径，换目录后会失效；必须用 `python3 -m venv` 重建 |
| API 路由前缀 | nginx 将 `/blog/api/` 代理到 `http://127.0.0.1:8001/api/`，后端路由以 `/api/` 开头 |
| 端口 | 后端固定 `8001`（8000 = 光学平台，8765 = 另一项目，8088 = threemaps）|
| exe 文件不进 git | `frontend/public/exes/*.zip` 已在 `.gitignore` 中排除 |

---

## 四、快速验证清单

部署完成后逐项检查：

- [ ] `https://www.optlab.space/blog/` 首页正常加载，页面跳转时出现水豚加载动画
- [ ] `https://www.optlab.space/blog/projects` 显示项目列表（从数据库加载）
- [ ] `https://www.optlab.space/blog/photos` 显示相册图片
- [ ] `https://www.optlab.space/blog/api/` 返回 `{"message":"起风了 API · 正在运行"}`
- [ ] `/blog/admin` 用管理员账号可以登录
- [ ] 后台仪表盘显示文章、评论、用户、AI 对话六维统计
- [ ] 后台图片上传测试：上传一张图片，相册页面可见
- [ ] 后台 `/blog/admin/exes` 能看到两个 zip 文件
- [ ] 下载按钮：点击项目卡片"⬇ 下载程序"，浏览器触发下载
- [ ] 水豚祁 AI 对话正常响应（流式输出）
- [ ] AI 对话 TTS：点击播放按钮，能听到阿里云 NLS 合成语音
- [ ] 后台 `/blog/admin/chat` 能查看用户聊天记录并支持清空
- [ ] 管理后台用户列表头像正常显示（非裂图）

---

## 五、常用命令速查

```bash
# 查看后端实时日志
journalctl -u qi-blog -f

# 重启后端
systemctl restart qi-blog

# 查看 nginx 错误日志
tail -f /var/log/nginx/error.log

# 测试后端 API
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8001/api/projects

# 检查端口监听
ss -tlnp | grep 8001

# 手动拉取最新代码并重启（后端更新一键命令）
cd /opt/qi-blog/repo && git pull && systemctl restart qi-blog && systemctl status qi-blog
```
