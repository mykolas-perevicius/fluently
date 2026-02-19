.PHONY: setup dev backend frontend ollama lint test check clean

# ── Setup ──────────────────────────────────────────────────
setup:
	@echo "📦 Setting up Fluently..."
	cp -n .env.example .env 2>/dev/null || true
	cd backend && uv sync
	cd frontend && npm install
	@echo "✅ Done. Run 'make dev' to start."

# ── Development ────────────────────────────────────────────
dev:
	@echo "🚀 Starting all services..."
	$(MAKE) -j3 backend frontend ollama

backend:
	cd backend && fastapi dev src/main.py

frontend:
	cd frontend && npm run dev

ollama:
	ollama serve

# ── Docker ─────────────────────────────────────────────────
up:
	docker compose up --build

down:
	docker compose down

# ── Quality ────────────────────────────────────────────────
lint:
	cd backend && uv run ruff check src/ && uv run black --check src/
	cd frontend && npm run lint

format:
	cd backend && uv run black src/ && uv run isort src/
	cd frontend && npx prettier --write src/

test:
	cd backend && uv run pytest
	cd frontend && npm run type-check

check: lint test
	@echo "✅ All checks passed."

# ── Cleanup ────────────────────────────────────────────────
clean:
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/node_modules frontend/dist
