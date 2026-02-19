# Fluently — Architecture

> Last updated: 2025-02-19
> Status: Living document — update as the system evolves.

---

## 1. Vision

Fluently is a "translate everything" platform. The value proposition is **not** raw translation quality (that's a commodity) — it's the **workflow around translation**: dead-simple UX, document-level intelligence, integrations, and price.

**Competitive thesis:**
- Translation alone is not a moat. Workflow + data + integrations can be.
- Offer cheaper + simpler integration than incumbents (Google Translate API, DeepL).
- Win on UX in specific niches (document translation, support ticket routing).
- Privacy-first: inference runs on our infrastructure, not third-party APIs.

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                          │
│              React + Vite + TailwindCSS                  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   Text   │  │  Image   │  │   PDF    │  ← input modes│
│  │  Editor  │  │  Upload  │  │  Upload  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       └──────────────┼──────────────┘                    │
│                      │ HTTP / SSE                        │
└──────────────────────┼──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                     API Gateway                           │
│                      FastAPI                              │
│                                                           │
│  ┌────────────────┐  ┌────────────────┐                  │
│  │ /translate/     │  │ /translate/    │                  │
│  │   (text)       │  │   image        │  ← routers       │
│  └───────┬────────┘  └───────┬────────┘                  │
│          │                   │                            │
│          ▼                   ▼                            │
│  ┌─────────────────────────────────────┐                 │
│  │          Service Layer              │                 │
│  │                                     │                 │
│  │  TranslationService                 │                 │
│  │  LanguageDetectionService           │                 │
│  │  DocumentService (future)           │                 │
│  └───────────────┬─────────────────────┘                 │
│                  │                                        │
│          ┌───────┴───────┐                               │
│          ▼               ▼                               │
│  ┌──────────────┐ ┌──────────────┐                       │
│  │   FastText   │ │  LLM Client  │                       │
│  │  (lang ID)   │ │ (translate)  │                       │
│  └──────────────┘ └──────┬───────┘                       │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
             ┌──────────┐  ┌──────────┐
             │  Ollama   │  │   vLLM   │
             │  (dev)    │  │  (prod)  │
             └──────────┘  └──────────┘
             TranslateGemma 12B
```

---

## 3. Backend Architecture

### 3.1 Layered Design

The backend follows a clean layered architecture to keep routers thin and logic testable:

```
routers/          → HTTP concerns only (validation, status codes, response shaping)
  ├── translate.py
  ├── documents.py    (future: PDF, DOCX)
  └── health.py

services/         → Business logic (stateless, injectable, testable)
  ├── translation.py  → prompt construction, LLM calls, response parsing
  ├── detection.py    → language detection via FastText
  ├── ocr.py          → image text extraction (future: Tesseract / vision model)
  └── document.py     → PDF parsing, layout preservation (future)

utils/            → Pure utilities (no side effects)
  ├── language.py     → LanguageCode enum, LANGUAGES map
  └── prompts.py      → prompt templates

dependencies.py   → FastAPI dependency injection (State, StateDep)
main.py           → App factory, lifespan, router registration
```

**Why a service layer?** Right now the translate router has LLM prompt construction baked in. Extracting that into services means: (a) routers stay thin, (b) services can be unit-tested without HTTP, (c) the same translation service powers text, image, and future document endpoints.

### 3.2 Translation Pipeline

```
Input text(s) → Language Detection → Prompt Construction → LLM Inference → Response Parsing → Output
                     │                       │
                     │                       ├── Model: TranslateGemma 12B
                     │                       └── Client: OpenAI-compatible API
                     │
                     ├── Model: FastText lid.176.bin
                     └── Threshold: 0.6827 confidence → fallback to English
```

**Key design decisions:**
- **OpenAI-compatible client**: The same `AsyncOpenAI` client works for both Ollama (dev) and vLLM (prod). Only `base_url` changes.
- **Sequential inference**: Currently translates texts one at a time in a loop. Batching is a priority optimization (see roadmap).
- **Confidence threshold**: 0.6827 (1σ) — if FastText isn't confident, default to English source.

### 3.3 Model Strategy

| Environment | Runtime | Model | Connection |
|-------------|---------|-------|------------|
| Development | Ollama | `translategemma:12b` | `localhost:11434/v1/` |
| Production | vLLM | `translategemma:12b` | Configured via `LLM_BASE_URL` env var |

TranslateGemma was chosen because it's purpose-built for translation (not a general chat model), supporting 100+ language pairs with high quality at 12B parameters.

### 3.4 Configuration Strategy

All configuration via environment variables (no config files):

```
# Core
LLM_BASE_URL=http://localhost:11434/v1/    # Ollama (dev) or vLLM (prod)
LLM_API_KEY=ollama                          # "ollama" for dev, real key for prod
LLM_MODEL=translategemma:12b

# FastText
FASTTEXT_MODEL_PATH=models/fasttext/lid.176.bin
DETECTION_CONFIDENCE_THRESHOLD=0.6827

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Future
REDIS_URL=redis://localhost:6379            # Caching layer
DATABASE_URL=                                # If/when we need persistence
```

---

## 4. Frontend Architecture

### 4.1 Design Philosophy

**"Google Translate, but better in specific ways."** The frontend should feel instant. No accounts, no sign-ups, no friction. You open it, you paste or upload, you get a translation.

### 4.2 Component Architecture

```
App
├── Layout
│   ├── Header (logo, nav)
│   └── Footer (links, language count)
│
├── Pages
│   ├── TranslatePage          ← main page, always visible
│   │   ├── InputPanel
│   │   │   ├── LanguageSelector (source)
│   │   │   ├── TextInput       ← textarea with char count
│   │   │   ├── ImageUpload     ← drag & drop zone
│   │   │   └── FileUpload      ← PDF/DOCX (future)
│   │   │
│   │   ├── SwapButton          ← swap source ↔ target
│   │   │
│   │   └── OutputPanel
│   │       ├── LanguageSelector (target)
│   │       ├── TranslationOutput ← result with copy button
│   │       └── LoadingState
│   │
│   └── AboutPage (optional)
│
├── Hooks
│   ├── useTranslation()       ← API call + debounce
│   ├── useLanguageDetect()    ← auto-detect display
│   └── useFileUpload()        ← drag/drop + validation
│
└── Services
    └── api.ts                 ← typed API client
```

### 4.3 API Client Design

The frontend API client should be a thin, typed wrapper:

```typescript
// services/api.ts — conceptual shape
const api = {
  translate: (texts: string[], target: LanguageCode, source?: LanguageCode) => Promise<string[]>,
  translateImage: (image: File, target: LanguageCode, source?: LanguageCode) => Promise<string>,
  // future:
  translateDocument: (file: File, target: LanguageCode) => Promise<Blob>,
}
```

---

## 5. Data Flow Patterns

### 5.1 Text Translation (current)

```
User types → debounce 300ms → POST /translate/ → display result
```

### 5.2 Image Translation (current)

```
User drops image → encode base64 → POST /translate/image → display extracted + translated text
```

### 5.3 PDF Translation (planned)

```
User uploads PDF → POST /translate/document → SSE progress stream → download translated PDF
```

### 5.4 Streaming (planned)

For long documents, the backend will stream progress via Server-Sent Events:

```
POST /translate/stream → SSE: { chunk: "translated segment", progress: 0.45 }
```

---

## 6. Deployment Architecture

### 6.1 Development

```
docker compose up
```

Runs: frontend (Vite dev server) + backend (FastAPI + uvicorn) + Ollama

### 6.2 Production (target)

```
                    ┌──────────┐
                    │  Caddy / │
  Users ──────────▶ │  Nginx   │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼                     ▼
      ┌──────────────┐     ┌──────────────┐
      │   Frontend   │     │   Backend    │
      │  (static /   │     │  (FastAPI    │
      │   CDN)       │     │   + uvicorn) │
      └──────────────┘     └──────┬───────┘
                                  │
                           ┌──────┴──────┐
                           ▼             ▼
                    ┌──────────┐  ┌──────────┐
                    │   vLLM   │  │  Redis   │
                    │ (GPU)    │  │ (cache)  │
                    └──────────┘  └──────────┘
```

---

## 7. Key Decisions Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Monorepo (backend + frontend) | Small team, shared CI, easier to keep in sync | 2025-02-19 |
| TranslateGemma 12B | Purpose-built for translation, good quality/size ratio | 2025-02 |
| OpenAI-compatible API client | Same code works for Ollama (dev) and vLLM (prod) | 2025-02 |
| FastText for lang detection | Fast, accurate, no GPU needed, 176 languages | 2025-02 |
| React + Vite (not Next.js) | SPA is fine — no SEO needed for a tool app | 2025-02-19 |
| No database initially | Stateless is simpler; add persistence when we need accounts/history | 2025-02-19 |
| Environment-based config | 12-factor app; no config files to manage across envs | 2025-02-19 |

---

## 8. Security Considerations

- **No auth (MVP)**: Public tool, no user accounts initially.
- **Rate limiting**: Needed before any public launch. Plan for IP-based rate limits via middleware or reverse proxy.
- **Input validation**: Max 50 texts per request, max 5MB images. Pydantic handles validation.
- **Base64 images**: Validate MIME type server-side before processing.
- **No data persistence**: Translations are not stored. Privacy by design.

---

## 9. Open Questions

- [ ] Do we want a caching layer (Redis) for repeated translations?
- [ ] Should the frontend support offline/PWA for the UI shell?
- [ ] What's the PDF parsing strategy? (PyMuPDF vs pdfplumber vs marker)
- [ ] Do we need accounts/history, or stay fully anonymous?
- [ ] Streaming: SSE or WebSockets?
