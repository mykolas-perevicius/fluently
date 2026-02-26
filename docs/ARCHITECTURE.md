# Fluently — Architecture

> Last updated: 2026-02-25
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
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ /translate/   │ │ /translate/  │ │  /pii/       │       │
│  │  (text)       │ │  image,      │ │  detect,     │ ← API │
│  │              │ │  document    │ │  redact      │       │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘       │
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
  ├── translate.py    → /translate/, /translate/image, /translate/document
  ├── pii.py          → /pii/detect, /pii/redact
  └── health.py

utils/            → Pure utilities and domain logic
  ├── language.py       → LanguageCode enum, LANGUAGES map
  ├── classifier.py     → Image text type classification (printed/handwritten)
  ├── ocr.py            → Tesseract OCR extraction
  ├── image.py          → Image processing (resize, format)
  ├── pdf_layout.py     → PyMuPDF layout extraction (headings, tables, lists)
  ├── format_renderers.py → Plaintext, Markdown, LaTeX renderers
  ├── pii_detector.py   → Hybrid PII detection (regex + LLM)
  └── pii_redactor.py   → PII redaction (mask, asterisk, synthetic)

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
│   ├── useTranslation()           ← text translation + debounce
│   ├── useImageTranslation()      ← image upload + OCR/vision pipeline
│   ├── useDocumentTranslation()   ← document extraction + plain/formatted translation
│   └── usePIIDetection()          ← PII scan, entity selection, redaction
│
└── Services
    └── api.ts                     ← typed API client (translate, translateImage,
                                      translateDocumentFormatted, detectPII, redactPII)
```

### 4.3 API Client Design

The frontend API client should be a thin, typed wrapper:

```typescript
// services/api.ts — actual shape
translateText(contents, targetLang, sourceLang?, signal?) → Promise<string[]>
translateImage(imageBase64, targetLang, sourceLang?) → Promise<{ text, textType }>
translateDocument(chunks, targetLang, sourceLang?, onProgress?, signal?) → Promise<string[]>
translateDocumentFormatted(file, targetLang, sourceLang?, signal?) → Promise<{ plaintext, markdown, latex, pageCount, blockCount }>
detectPII(text) → Promise<{ entities: PIIEntity[] }>
redactPII(text, entities, strategy) → Promise<{ redacted_text, redaction_count }>
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

### 5.3 PDF Document Translation (live)

```
User uploads PDF → POST /translate/document (multipart)
  → PyMuPDF extracts structured blocks (headings, paragraphs, lists, tables)
  → Font-size histogram classifies headings vs body text
  → Blocks batched (groups of 50) → translated via asyncio.gather
  → Three renderers produce plaintext / markdown / latex
  → JSON response with all three formats + metadata
Frontend shows format tabs: [Plain] [Markdown] [LaTeX] with download buttons
```

### 5.4 PII Detection & Redaction (live)

```
User enables PII toggle → POST /pii/detect sends extracted text
  → Regex pass: emails, phones, SSNs, credit cards, IPs (confidence: 0.95)
  → LLM pass: names, addresses, organizations (parallel with regex)
  → Deduplicate overlapping spans (prefer higher confidence)
  → Frontend highlights entities, user confirms which to redact
  → POST /pii/redact applies chosen strategy (mask/asterisk/synthetic)
  → Redacted text fed into translation pipeline
```

### 5.5 Streaming (planned)

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
| PyMuPDF for PDF extraction | Rich font metadata (size, bold, italic), fast, well-maintained | 2026-02-25 |
| Three output formats | Plaintext for quick copy, Markdown for docs, LaTeX for academic use | 2026-02-25 |
| Hybrid PII detection | Regex for structured PII (fast, high confidence) + LLM for contextual (names, addresses) | 2026-02-25 |
| PII runs pre-translation | User reviews entities before translation runs, keeping control over what gets redacted | 2026-02-25 |

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
- [x] ~~What's the PDF parsing strategy?~~ → **PyMuPDF** chosen: `page.get_text("dict")` provides font metadata + bounding boxes for layout classification
- [ ] Do we need accounts/history, or stay fully anonymous?
- [ ] Streaming: SSE or WebSockets?
