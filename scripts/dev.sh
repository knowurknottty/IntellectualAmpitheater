#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export INTELAMP_DATABASE_URL="${INTELAMP_DATABASE_URL:-sqlite+aiosqlite:///$ROOT/intelamp.sqlite3}"
cleanup() { [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
(
  cd backend
  INTELAMP_DATABASE_URL="$INTELAMP_DATABASE_URL" uv run alembic upgrade head
  exec uv run uvicorn intelamp.app:create_app_from_env --factory --host 127.0.0.1 --port 8787
) &
BACKEND_PID=$!
for _ in {1..80}; do
  if curl -fsS http://127.0.0.1:8787/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done
curl -fsS http://127.0.0.1:8787/api/health >/dev/null
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
