#!/usr/bin/env bash
set -euo pipefail

# Simple launcher for backend (FastAPI) and frontend (Vite) in separate terminals
# Prerequisites: .venv with deps installed, npm install in podcast_engine/frontend

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_CMD="source ${ROOT_DIR}/.venv/bin/activate && uvicorn podcast_engine.backend.app:app --host 0.0.0.0 --port 8000 --reload"
FRONTEND_CMD="cd ${ROOT_DIR}/podcast_engine/frontend && npm run dev"

backend() {
  echo "Starting backend on :8000"
  bash -c "${BACKEND_CMD}"
}

frontend() {
  echo "Starting frontend on :5173"
  bash -c "${FRONTEND_CMD}"
}

# If tmux is available, use two panes; otherwise run backend in background and frontend in foreground.
if command -v tmux >/dev/null 2>&1; then
  tmux new-session -d -s podcast_engine "${BACKEND_CMD}" \; split-window -h "${FRONTEND_CMD}" \; select-pane -t 0 \; attach -t podcast_engine
else
  echo "tmux not found; starting backend in background and frontend in foreground."
  bash -c "${BACKEND_CMD}" &
  FRONT_PID=$!
  trap "kill ${FRONT_PID} 2>/dev/null" EXIT
  bash -c "${FRONTEND_CMD}"
fi
