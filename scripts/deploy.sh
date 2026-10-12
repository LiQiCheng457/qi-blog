#!/bin/bash
# qi-blog 一键部署脚本（在服务器上以 root 运行）
#
# 用法:
#   ./scripts/deploy.sh                  # 构建前端 + 备份 + 发布 + 健康检查
#   ./scripts/deploy.sh --skip-build     # 跳过构建，直接发布 repo/frontend/dist
#   ./scripts/deploy.sh --restart-backend # 发布后重启后端（改了后端代码时加）
#   ./scripts/deploy.sh --migrate        # 发布前执行 alembic upgrade head（改了表结构时加）
#
# 依赖: /opt/node-v20.18.1-linux-x64（Node 20，系统自带 Node 12 跑不了 Vite 5）
set -euo pipefail

REPO=/opt/qi-blog/repo
DEPLOY_DIR=/var/www/qi-blog/dist
BACKUP_DIR=/var/backups/qiblog/dist
export PATH=/opt/node-v20.18.1-linux-x64/bin:$PATH

SKIP_BUILD=0
RESTART_BACKEND=0
MIGRATE=0
for arg in "$@"; do
    case $arg in
        --skip-build)      SKIP_BUILD=1 ;;
        --restart-backend) RESTART_BACKEND=1 ;;
        --migrate)         MIGRATE=1 ;;
        *) echo "未知参数: $arg"; exit 1 ;;
    esac
done

echo "==> [1/5] 构建前端"
if [ "$SKIP_BUILD" -eq 0 ]; then
    cd "$REPO/frontend"
    [ -d node_modules ] || npm install --no-audit --no-fund
    npm run build
else
    echo "    跳过（使用现有 $REPO/frontend/dist）"
fi

echo "==> [2/5] 备份当前线上 dist"
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
tar -czf "$BACKUP_DIR/dist-$STAMP.tgz" -C /var/www/qi-blog dist
ls -1t "$BACKUP_DIR"/dist-*.tgz | tail -n +4 | xargs -r rm -f   # 只留最近3份
echo "    备份: $BACKUP_DIR/dist-$STAMP.tgz"

echo "==> [3/5] 数据库迁移"
if [ "$MIGRATE" -eq 1 ]; then
    su -s /bin/bash qiblog -c "cd $REPO/backend && .venv/bin/alembic upgrade head"
else
    echo "    跳过"
fi

echo "==> [4/5] 发布到 $DEPLOY_DIR"
rsync -a --delete "$REPO/frontend/dist/" "$DEPLOY_DIR/"

if [ "$RESTART_BACKEND" -eq 1 ]; then
    systemctl restart qi-blog
    sleep 3
fi

echo "==> [5/5] 健康检查"
sleep 1
PAGE=$(curl -s -o /dev/null -w '%{http_code}' https://www.optlab.space/blog/)
API=$(curl  -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8001/api/posts)
echo "    页面: $PAGE  API: $API"

if [ "$PAGE" = "200" ] && [ "$API" = "200" ]; then
    echo "✅ 部署完成"
else
    echo "❌ 健康检查未通过！可回滚："
    echo "    rsync 之前先解包备份: tar -xzf $BACKUP_DIR/dist-$STAMP.tgz -C /var/www/qi-blog"
    exit 1
fi
