# 起风了博客当前服务器部署说明

本文档记录 2026-06-14 当前线上服务器的实际部署状态，用于后续 agent 快速熟悉环境。它描述的是服务器现状，不是首次部署教程。

## 1. 访问入口

博客当前有两个可用入口：

- 域名入口：`https://www.optlab.space/blog/`
- IP 入口：`http://47.116.111.170/blog/`

以下入口不属于博客：

- `https://www.optlab.space/`：原光学综合平台主站。
- `http://47.116.111.170/`：原光学综合平台主站。
- `http://47.116.111.170:8088/`：ThreeMaps energy 项目，不是博客。

注意：浏览器地址栏可能缓存旧标题。如果 `http://47.116.111.170/blog/` 地址栏建议仍显示“光学综合平台”，以实际页面 HTML 为准，必要时用无痕窗口或 `Ctrl + F5`。

## 2. 服务器上的项目分布

服务器：`47.116.111.170`

当前主要项目：

| 项目 | 路径 | 服务/端口 | 说明 |
| --- | --- | --- | --- |
| 光学综合平台 | `/opt/optical-lab-platform`、`/var/www/optical/dist` | `optical-backend.service`，`127.0.0.1:8000` | 根路径主站 |
| 起风了博客 | `/opt/qi-blog`、`/var/www/qi-blog` | `qi-blog.service`，`127.0.0.1:8001` | 本文档描述的博客 |
| ThreeMaps energy | `/opt/threemaps-energy` | `threemaps-prediction.service`，`127.0.0.1:8765`；nginx `8088` | 不要把 8088 改给博客 |

## 3. 博客目录结构

```text
/var/www/qi-blog/
├── dist/          # 前端 Vite 构建产物，由 nginx 静态服务
├── photos/        # 用户上传图片、项目图片，持久化，不随前端覆盖
└── exes/          # exe/zip 下载包，持久化，不随前端覆盖

/opt/qi-blog/
├── backend/       # FastAPI 后端代码
│   ├── .env       # 生产环境变量，不要覆盖
│   ├── .venv/     # Python 虚拟环境
│   ├── main.py
│   ├── routers/
│   └── requirements.txt
└── backups/       # 部署/配置修改前的备份
```

## 4. nginx 配置

nginx 主配置文件实际来自：

```text
/opt/optical-lab-platform/deploy-local/nginx-site.conf
```

该文件通过 `/etc/nginx/sites-enabled/optical` 生效。

博客相关 location 同时配置在两个 server block：

- `server_name www.optlab.space optlab.space` 的 `443 ssl` server：支持 `https://www.optlab.space/blog/`
- `server_name 47.116.111.170` 的 `80` server：支持 `http://47.116.111.170/blog/`

关键规则：

```nginx
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

location ^~ /photos/ {
    alias /var/www/qi-blog/photos/;
    expires 30d;
}

location ^~ /animations/ {
    alias /var/www/qi-blog/dist/animations/;
    expires 30d;
}

location ^~ /exes/ {
    alias /var/www/qi-blog/exes/;
    add_header Content-Disposition attachment;
}
```

`^~ /blog/` 很重要，用来避免通用静态资源正则把 `/blog/assets/*.js`、`/blog/*.ico` 等请求截到光学平台目录。

## 5. 后端服务

systemd 服务名：

```bash
qi-blog.service
```

实际启动命令：

```bash
/opt/qi-blog/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 1
```

后端只监听本机 `127.0.0.1:8001`，公网通过 nginx 的 `/blog/api/` 反向代理访问：

- 外部：`https://www.optlab.space/blog/api/projects`
- nginx 转发：`http://127.0.0.1:8001/api/projects`

生产 `.env` 在：

```text
/opt/qi-blog/backend/.env
```

不要在部署时覆盖 `.env` 和 `.venv`。

## 6. 前端资源加载

前端是 Vite + Vue SPA，构建 base 为 `/blog/`。

生产构建后的资源路径：

| 资源 | 线上路径 | 服务器文件 |
| --- | --- | --- |
| HTML | `/blog/` | `/var/www/qi-blog/dist/index.html` |
| JS/CSS | `/blog/assets/...` | `/var/www/qi-blog/dist/assets/...` |
| favicon | `/blog/favicon.ico` | `/var/www/qi-blog/dist/favicon.ico` |
| 固定头像 | `/blog/avatars/...` | `/var/www/qi-blog/dist/avatars/...` |
| 水豚动画 | `/blog/animations/...` | `/var/www/qi-blog/dist/animations/...` |
| 相册/项目图片 | `/photos/...` | `/var/www/qi-blog/photos/...` |
| 下载包 | `/exes/...` | `/var/www/qi-blog/exes/...` |

前端代码里需要注意：

- `frontend/index.html` 的 favicon 使用 `%BASE_URL%favicon.ico`，构建后为 `/blog/favicon.ico`。
- 站内静态资源应通过 `frontend/src/utils/assets.ts` 的 `assetUrl()` 处理，避免写死 `/avatars/...` 或 `/animations/...`。
- 后台“查看博客”应使用 `RouterLink to="/"`，不要写 `<a href="/">`，否则会跳到主站根路径。

## 7. 数据与持久化资源

数据库中常见 URL 字段：

- 图片：`/photos/xxx.png`
- 下载包：`/exes/xxx.zip`
- 用户头像：`/avatars/qi-avatar-xxx.png`

其中：

- `/photos/...` 由 nginx 直接映射到 `/var/www/qi-blog/photos/`
- `/exes/...` 由 nginx 直接映射到 `/var/www/qi-blog/exes/`
- `/avatars/...` 是前端内置资源，渲染时通过 `assetUrl()` 变成 `/blog/avatars/...`

部署前端时不要用会删除 `/var/www/qi-blog/photos` 或 `/var/www/qi-blog/exes` 的命令。只替换 `/var/www/qi-blog/dist`。

## 8. 已修复过的问题

### 登录 500

原因：服务器曾安装 `bcrypt 5.0.0`，与 `passlib 1.7.4` 不兼容，登录时在 `verify_password()` 中抛 500。

处理：

- 服务器虚拟环境已安装 `bcrypt==4.0.1`
- `backend/requirements.txt` 已钉住：

```text
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
```

### 用户头像不显示

原因：头像保存为 `/avatars/...`，部署在 `/blog/` 子路径时会请求站点根路径。

处理：新增 `frontend/src/utils/assets.ts`，渲染时把站内静态资源加上 Vite base。

### favicon 显示成主站图标

原因：`frontend/index.html` 原来写死 `/favicon.ico`。

处理：改成 `%BASE_URL%favicon.ico`。

### 后台“查看博客”跳到主站

原因：后台布局里原来写 `<a href="/">查看博客</a>`。

处理：改成 `RouterLink to="/" target="_blank"`。

### IP `/blog/` 返回基础站

原因：最初只在域名 HTTPS server block 配了博客 location，IP 的 80 server block 没有。

处理：已把博客 location 同步加入 `server_name 47.116.111.170` 的 80 server block。

## 9. 常用运维命令

查看后端状态：

```bash
systemctl status qi-blog
```

重启后端：

```bash
systemctl restart qi-blog
```

查看后端日志：

```bash
journalctl -u qi-blog -f
```

检查 nginx 配置：

```bash
nginx -t
```

重载 nginx：

```bash
systemctl reload nginx
```

检查监听端口：

```bash
ss -tlnp
```

## 10. 推荐更新流程

### 只更新前端

本机：

```bash
cd frontend
npm run build
```

上传时只同步 `frontend/dist/` 到服务器 `/var/www/qi-blog/dist/`。不要覆盖 `/var/www/qi-blog/photos/` 或 `/var/www/qi-blog/exes/`。

建议部署前先备份：

```bash
ts=$(date +%Y%m%d-%H%M%S)
tar -C /var/www/qi-blog -czf /opt/qi-blog/backups/dist-$ts.tgz dist
```

### 只更新后端

替换 `/opt/qi-blog/backend` 中源码文件，保留：

- `/opt/qi-blog/backend/.env`
- `/opt/qi-blog/backend/.venv`

然后：

```bash
cd /opt/qi-blog/backend
.venv/bin/pip install -r requirements.txt
systemctl restart qi-blog
systemctl status qi-blog
```

### 修改 nginx

先备份：

```bash
ts=$(date +%Y%m%d-%H%M%S)
cp /opt/optical-lab-platform/deploy-local/nginx-site.conf \
   /opt/optical-lab-platform/deploy-local/nginx-site.conf.bak-$ts
```

修改后：

```bash
nginx -t
systemctl reload nginx
```

## 11. 快速验收清单

```bash
curl -I https://www.optlab.space/blog/
curl -I http://47.116.111.170/blog/
curl -I https://www.optlab.space/blog/favicon.ico
curl -I http://47.116.111.170/blog/favicon.ico
curl https://www.optlab.space/blog/api/projects
curl http://47.116.111.170/blog/api/projects
curl -I https://www.optlab.space/photos/Platform.png
curl -I http://47.116.111.170/photos/Platform.png
```

预期：

- `/blog/` 返回博客 `index.html`
- `/blog/favicon.ico` 返回博客图标
- `/blog/api/projects` 返回 JSON
- `/photos/...` 返回图片
- `qi-blog.service` 为 `active`

