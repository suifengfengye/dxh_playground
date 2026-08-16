#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MONOREPO_DIR="$(cd "${SOURCE_PROJECT_DIR}/.." && pwd)"

TARGET_DIR="${TARGET_DIR:-${HOME}/ai-trend}"
DATA_DIR="${DATA_DIR:-/data/ai-trend}"
ENV_FILE_SOURCE="${ENV_FILE_SOURCE:-${HOME}/.env}"
COMPOSE_CMD="${COMPOSE_CMD:-docker compose}"

echo "==> Pull latest code from monorepo"
git -C "${MONOREPO_DIR}" pull

echo "==> Ensure target directory exists"
mkdir -p "${TARGET_DIR}"
mkdir -p "${DATA_DIR}"

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required but not installed"
  exit 1
fi

echo "==> Sync ai-trend project to target directory"
rsync -a --delete \
  --exclude ".git/" \
  --exclude ".env" \
  --exclude "frontend/.next/" \
  --exclude "frontend/node_modules/" \
  --exclude "backend/__pycache__/" \
  --exclude "backend/.pytest_cache/" \
  --exclude "backend/.ruff_cache/" \
  "${SOURCE_PROJECT_DIR}/" "${TARGET_DIR}/"

if [[ -f "${ENV_FILE_SOURCE}" ]]; then
  echo "==> Copy deployment env file"
  cp "${ENV_FILE_SOURCE}" "${TARGET_DIR}/.env"
else
  echo "Env file not found: ${ENV_FILE_SOURCE}"
  exit 1
fi

cd "${TARGET_DIR}"

echo "==> Stop running containers and remove compose-built images"
${COMPOSE_CMD} down --remove-orphans --rmi local

echo "==> Rebuild images without cache"
${COMPOSE_CMD} build --no-cache

echo "==> Start services"
${COMPOSE_CMD} up -d --force-recreate --remove-orphans

echo "==> Deployment finished"
${COMPOSE_CMD} ps
