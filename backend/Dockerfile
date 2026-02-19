# ── Build stage ────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Build tools for compiling fasttext's C++ extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* .

# Pre-install pybind11<3 (fasttext 0.9.3 is incompatible with pybind11>=3)
RUN uv venv && uv pip install 'pybind11<3'
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

COPY . .

# ── Runtime stage ─────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app /app

EXPOSE 8000

CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
