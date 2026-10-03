#!/usr/bin/env bash
# 启动 demo。端口默认 8391，避开 8000/8080/5000/7000 这些常被占用的。
# 想换端口：PORT=9000 ./run.sh
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8391}"

if [ ! -x .venv/bin/uvicorn ]; then
  echo "缺少依赖，请先执行：" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

echo "→ 打开 http://localhost:${PORT}"
echo "→ 录屏自动开跑：http://localhost:${PORT}/?autorun"
echo

exec .venv/bin/uvicorn server:app --port "${PORT}" "$@"
