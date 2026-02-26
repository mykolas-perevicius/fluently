#!/usr/bin/env bash
# Fluently development runner — starts all services and ensures clean shutdown on Ctrl+C.
# Models are unloaded from RAM (but stay cached on disk) when the backend shuts down.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDS=()
OLLAMA_STARTED_BY_US=false

cleanup() {
    echo ""
    echo "Shutting down Fluently..."

    # Kill child processes (backend & frontend)
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null
        fi
    done

    # Wait for backend to finish its graceful model unloading
    for pid in "${PIDS[@]}"; do
        wait "$pid" 2>/dev/null || true
    done

    # If we started Ollama, stop it too
    if $OLLAMA_STARTED_BY_US; then
        echo "Stopping Ollama..."
        pkill -f "ollama serve" 2>/dev/null || true
    fi

    echo "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# ── Start Ollama (if not already running) ──────────────────────────
if ollama list >/dev/null 2>&1; then
    echo "Ollama already running."
else
    echo "Starting Ollama..."
    ollama serve &
    OLLAMA_STARTED_BY_US=true
    # Give it a moment to bind the port
    sleep 2
fi

# ── Start backend ──────────────────────────────────────────────────
echo "Starting backend..."
cd "$ROOT/backend" && uv run fastapi dev src/main.py &
PIDS+=($!)

# ── Start frontend ─────────────────────────────────────────────────
echo "Starting frontend..."
cd "$ROOT/frontend" && npm run dev &
PIDS+=($!)

echo ""
echo "Fluently is running. Press Ctrl+C to stop all services."
echo ""

# Wait for any child to exit (or for the trap to fire)
wait
