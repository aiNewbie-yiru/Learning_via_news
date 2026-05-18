#!/bin/bash

echo "=== 英语学习工具启动脚本 ==="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 设置代理：抓取 BBC 等外网新闻需要代理；本机前后端接口通过 NO_PROXY 排除
export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1}"
PROXY_URL="${PROXY_URL:-http://127.0.0.1:7890}"
export HTTPS_PROXY="$PROXY_URL"
export HTTP_PROXY="$PROXY_URL"
export https_proxy="$PROXY_URL"
export http_proxy="$PROXY_URL"
export no_proxy="$NO_PROXY"
echo "代理已设置: $PROXY_URL"
echo "本机地址不走代理: $NO_PROXY"

# 启动后端服务
echo "[1/2] 启动后端服务..."
cd "$BACKEND_DIR"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"
echo ""

# 等待一下确保后端启动
sleep 2

# 启动前端服务
echo "[2/2] 启动前端服务..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo ""

echo "=== 启动完成 ==="
echo "后端服务: http://localhost:8000"
echo "前端服务: http://localhost:3000（若 3000 被占用，请以 npm 输出的 Local 地址为准）"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
wait
