<div align="center">

# Fluently

**Translate everything. Privately.**

A fast, privacy-first translation platform for text, images, and documents — powered by local AI inference.

No data leaves your infrastructure. No per-character billing. No accounts required.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-3776AB?logo=python&logoColor=white)](#tech-stack)
[![React 19](https://img.shields.io/badge/react-19-61DAFB?logo=react&logoColor=black)](#tech-stack)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-009688?logo=fastapi&logoColor=white)](#tech-stack)
[![License](https://img.shields.io/badge/license-TBD-lightgrey)](#license)

---

[Features](#features) · [Quick Start](#quick-start-macos) · [Architecture](#architecture) · [API](#api-endpoints) · [Docs](#documentation) · [Contributing](#contributing)

</div>

---

## Features

| Capability | Status | Description |
|:-----------|:------:|:------------|
| **Text translation** | ✅ | Batch translate up to 50 strings per request with auto language detection |
| **Image translation** | ✅ | Extract + translate text from images via OCR and handwriting vision AI |
| **Document translation** | ✅ | PDF layout extraction with formatted output in Plain, Markdown, and LaTeX |
| **PII detection & redaction** | ✅ | Hybrid regex + AI detection with mask, asterisk, or synthetic redaction |
| **Language detection** | ✅ | FastText-based auto-detection across 176 languages |
| **Streaming** | 📋 | Server-sent events for long translations (planned) |

---

## Quick Start (macOS)

### Prerequisites

Install system dependencies with [Homebrew](https://brew.sh):

```bash
brew install uv node ollama tesseract
```

| Tool | Purpose |
|:-----|:--------|
| **[uv](https://github.com/astral-sh/uv)** | Python package manager (installs Python 3.14 automatically) |
| **[Node.js](https://nodejs.org/) 20+** | Frontend toolchain |
| **[Ollama](https://ollama.com/)** | Local LLM inference |
| **[Tesseract](https://github.com/tesseract-ocr/tesseract)** | OCR engine for printed text extraction |

### One-command setup

```bash
git clone https://github.com/<org>/fluently.git
cd fluently
make setup        # installs Python + Node deps, copies .env
```

### Pull the translation model

```bash
ollama pull translategemma:12b
```

> This downloads ~7 GB. You only need to do this once — the model stays cached on disk.

### Start everything

```bash
make dev
```

This runs **Ollama + Backend + Frontend** in one terminal with clean `Ctrl+C` shutdown.

| Service | URL |
|:--------|:----|
| Frontend | [`http://localhost:5173`](http://localhost:5173) |
| Backend API | [`http://localhost:8000`](http://localhost:8000) |
| API Docs (Swagger) | [`http://localhost:8000/docs`](http://localhost:8000/docs) |

### Alternative: Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

### Alternative: Manual (separate terminals)

```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Backend
cd backend && uv run fastapi dev src/main.py

# Terminal 3 — Frontend
cd frontend && npm run dev
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                          │
│              React 19 + Vite + TailwindCSS               │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │   Text   │  │  Image   │  │   PDF    │  ← input modes │
│  │  Editor  │  │  Upload  │  │  Upload  │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       └──────────────┼──────────────┘                    │
│                      │ HTTP                              │
└──────────────────────┼───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│                                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│  │ /translate/   │ │ /translate/  │ │  /pii/       │      │
│  │  text         │ │  image,      │ │  detect,     │      │
│  │               │ │  document    │ │  redact      │      │
│  └──────┬────────┘ └──────┬──────┘ └──────┬───────┘      │
│         │                 │               │               │
│         ▼                 ▼               ▼               │
│  ┌────────────────────────────────────────────────┐      │
│  │              Service Layer                      │      │
│  │                                                 │      │
│  │  Translation · Language Detection · PII · PDF   │      │
│  └───────────────────┬─────────────────────────────┘      │
│                      │                                    │
│          ┌───────────┼───────────┐                        │
│          ▼           ▼           ▼                        │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐                │
│  │  FastText   │ │  LLM     │ │ Tesseract │               │
│  │  (lang ID)  │ │  Client  │ │  (OCR)    │               │
│  └────────────┘ └────┬─────┘ └──────────┘                │
│                      │                                    │
└──────────────────────┼────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                ▼             ▼
         ┌──────────┐  ┌──────────┐
         │  Ollama   │  │   vLLM   │
         │  (dev)    │  │  (prod)  │
         └──────────┘  └──────────┘
              TranslateGemma 12B
```

<div align="center">

*Full architecture deep-dive: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)*

</div>

---

## API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/translate/` | Translate an array of text strings |
| `POST` | `/translate/image` | Extract and translate text from an image |
| `POST` | `/translate/document` | Translate a PDF with layout-aware formatting (Plain, Markdown, LaTeX) |
| `POST` | `/pii/detect` | Detect PII using hybrid regex + LLM |
| `POST` | `/pii/redact` | Redact PII with mask, asterisk, or synthetic strategy |
| `GET`  | `/health` | Liveness check |

<div align="center">

*Full API reference with request/response examples: [`docs/API.md`](docs/API.md)*

</div>

---

## Project Structure

```
fluently/
├── backend/                ← FastAPI translation API (Python 3.14)
│   ├── src/
│   │   ├── routers/            translate.py · pii.py · health.py
│   │   ├── utils/              language detection · OCR · PDF layout
│   │   │                       format renderers · PII detector/redactor
│   │   ├── main.py             app factory + lifespan
│   │   ├── config.py           env-based configuration
│   │   └── dependencies.py     FastAPI dependency injection
│   └── tests/              ← 133 unit tests
│
├── frontend/               ← React 19 + Vite + TailwindCSS (TypeScript)
│   └── src/
│       ├── components/         TranslatePage · DocumentTranslatePanel
│       │                       ImageTranslatePanel · LandingPage
│       ├── hooks/              useTranslation · useImageTranslation
│       │                       useDocumentTranslation · usePIIDetection
│       ├── services/           api.ts (typed API client)
│       └── types/              shared TypeScript interfaces
│
├── docs/                   ← Architecture, API reference, roadmap
├── scripts/                ← Dev runner, test materials, Playwright walkthrough
├── Makefile                ← make setup · make dev · make test · make lint
├── docker-compose.yml
├── .env.example
└── CONTRIBUTING.md
```

---

## Data Flow

### Text Translation

```
User types → debounce 300ms → POST /translate/ → display result
```

### Image Translation

```
User drops image → base64 encode → POST /translate/image
  → Classifier picks pipeline: Tesseract OCR (printed) or Vision model (handwritten)
  → Translate extracted text → display
```

### Document Translation (PDF)

```
User uploads PDF → POST /translate/document (multipart)
  → PyMuPDF extracts structured blocks (headings, paragraphs, lists, tables)
  → Font-size histogram classifies headings vs body text
  → Blocks batched (groups of 50) → translated via asyncio.gather
  → Three renderers produce plaintext / markdown / LaTeX
  → Frontend shows format tabs with download buttons
```

### PII Detection & Redaction

```
User enables PII toggle → POST /pii/detect
  → Regex pass: emails, phones, SSNs, credit cards, IPs
  → LLM pass: names, addresses, organizations (in parallel)
  → User reviews & confirms entities → POST /pii/redact
  → Redacted text fed into translation pipeline
```

---

## Tech Stack

<div align="center">

| Layer | Technology |
|:------|:-----------|
| **Backend** | FastAPI · Python 3.14 · FastText · PyMuPDF · Tesseract · Ollama / vLLM |
| **Frontend** | React 19 · TypeScript · Vite · TailwindCSS |
| **AI Model** | TranslateGemma 12B (100+ language pairs) |
| **Infra** | Docker Compose · GitHub Actions |

</div>

---

## Make Commands

```bash
make setup      # Install all dependencies, copy .env
make dev        # Start Ollama + backend + frontend (one terminal)
make test       # Run backend pytest + frontend type-check
make lint       # Ruff + Black (backend) + ESLint (frontend)
make format     # Auto-format all code
make check      # lint + test combined
make up         # Docker Compose up --build
make down       # Docker Compose down
make clean      # Remove caches and build artifacts
```

---

## Documentation

| Document | Description |
|:---------|:------------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, component architecture, data flows, key decisions |
| [`docs/API.md`](docs/API.md) | Full API reference with request/response examples |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Feature roadmap across 5 phases |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch strategy, dev workflow, code style |
| [`backend/`](backend/) | Backend-specific setup and development |
| [`frontend/`](frontend/) | Frontend-specific setup and development |

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branch strategy, workflow, and code style guidelines.

```bash
# Quick contribution flow
git checkout -b feat/your-feature dev
# ... make changes ...
make check                    # lint + test before pushing
git push -u origin feat/your-feature
# Open PR → dev
```

---

## License

TBD — See individual component licenses in `backend/` and `frontend/`.

The FastText language identification model (`lid.176.bin`) is distributed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
