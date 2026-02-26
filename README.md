# Fluently

**Translate everything.** A fast, privacy-first translation platform that handles text, images, and documents — powered by local AI inference.

Fluently combines a dead-simple frontend with a sophisticated backend to deliver cheap, fast, high-quality translation. No data leaves your infrastructure. No per-character billing surprises.

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [uv](https://github.com/astral-sh/uv) | latest | Python dependency management |
| [Node.js](https://nodejs.org/) | 20+ | Frontend toolchain |
| [Ollama](https://ollama.com/) | latest | Local LLM inference (dev) |
| [Docker](https://www.docker.com/) | 24+ | Optional: containerized dev |

### Option A: Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up
```

Frontend: `http://localhost:5173` · Backend: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

### Option B: Manual Setup

**Backend:**

```bash
cd backend
uv sync
ollama pull translategemma:12b
ollama serve                     # in a separate terminal
fastapi dev src/main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
fluently/
├── backend/          ← FastAPI translation API (Python)
├── frontend/         ← React + Vite SPA (TypeScript)
├── docs/             ← Architecture, roadmap, API specs
├── .github/          ← CI/CD workflows
├── docker-compose.yml
├── Makefile          ← Common dev commands
└── CONTRIBUTING.md   ← How to work in this repo
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design, [docs/ROADMAP.md](docs/ROADMAP.md) for what's planned, and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow.

---

## What Fluently Does

| Capability | Status | Description |
|------------|--------|-------------|
| **Text translation** | ✅ Live | Batch translate up to 50 strings per request |
| **Image translation** | ✅ Live | Extract + translate text from images (OCR + handwriting AI) |
| **Document translation** | ✅ Live | PDF layout extraction with formatted output (Plain, Markdown, LaTeX) |
| **PII detection & redaction** | ✅ Live | Hybrid regex + AI detection with mask, asterisk, or synthetic redaction |
| **Language detection** | ✅ Live | FastText-based auto-detection (176 languages) |
| **Streaming** | 📋 Planned | Server-sent events for long translations |

---

## Tech Stack

**Backend:** FastAPI · Python 3.14+ · FastText · PyMuPDF · Ollama (dev) / vLLM (prod) · TranslateGemma 12B

**Frontend:** React 19 · TypeScript · Vite · TailwindCSS

**Infra:** Docker Compose · GitHub Actions

---

## License

TBD — See individual component licenses in `backend/` and `frontend/`.

The FastText language identification model (`lid.176.bin`) is distributed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
