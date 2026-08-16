# AI Trend MVP

一个面向 AI 开源仓库的轻量 watchlist + 趋势监控工具。

## 技术栈

- Backend: FastAPI + SQLite + APScheduler
- Frontend: Next.js + TypeScript + Tailwind + shadcn/ui 风格基础组件
- Deploy: Docker Compose

## 目录

- `backend/`: FastAPI API 与定时采集任务
- `frontend/`: Next.js 前端页面
- `data/`: SQLite 数据文件
- `docs/`: 调研、方案、竞品和架构文档
- `scripts/`: 独立 demo 与实验脚本
- `docker-compose.yml`: 本地开发与部署入口

## 后端启动

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 第一版 API

- `POST /api/watchlist`
- `GET /api/watchlist`
- `GET /api/repos/{id}`
- `GET /api/repos/{id}/metrics`
- `GET /api/dashboard/summary`

## 下一步建议

1. 接入 ECharts 做折线图
2. 加 `POST /repos/{id}/collect` 手动采集接口
3. 补 7d / 30d 增长与 breakout score
4. 补 Alembic 迁移与前端删除功能
