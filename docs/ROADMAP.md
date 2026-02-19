# Fluently — Roadmap

> Last updated: 2025-02-19

---

## Phase 0: Foundation (← you are here)

**Goal:** Monorepo scaffold, docs, working dev environment, starter frontend.

- [x] Backend: text translation endpoint (`POST /translate/`)
- [x] Backend: image translation endpoint (`POST /translate/image`)
- [x] Language detection via FastText (176 languages)
- [x] OpenAPI schema published
- [ ] Monorepo structure (backend + frontend + docs)
- [ ] Docker Compose dev environment
- [ ] CI pipeline (lint + test)
- [ ] Starter frontend with text translation working

---

## Phase 1: MVP — "Translate Everything" Web App

**Goal:** A public-facing tool where anyone can translate text, images, and PDFs with zero friction.

### Frontend
- [ ] Text translation with debounced auto-translate
- [ ] Language auto-detection indicator ("Detected: French")
- [ ] Source ↔ target language swap
- [ ] Image upload with drag & drop
- [ ] Image translation result display
- [ ] Copy-to-clipboard on output
- [ ] Mobile-responsive layout
- [ ] Dark mode

### Backend
- [ ] Refactor: extract service layer from routers
- [ ] Environment-based configuration (no hardcoded URLs)
- [ ] Health check endpoint (`GET /health`)
- [ ] Request validation hardening (file size limits, content-type checks)
- [ ] Basic request logging / structured logging
- [ ] Error handling standardization

### Infra
- [ ] Docker Compose: frontend + backend + Ollama
- [ ] GitHub Actions: lint (ruff/black + eslint), type-check (pyright + tsc), test
- [ ] `.env.example` with all config documented

---

## Phase 2: PDF Translation

**Goal:** "One step closer to full PDF translation." Upload a PDF, get a translated PDF back.

### Backend
- [ ] PDF text extraction (PyMuPDF or pdfplumber)
- [ ] Page-by-page translation pipeline
- [ ] Layout-aware translation (preserve formatting where possible)
- [ ] Translated PDF generation
- [ ] `POST /translate/document` endpoint
- [ ] Progress reporting via SSE for long documents
- [ ] File size limits and page count limits

### Frontend
- [ ] PDF upload UI (drag & drop)
- [ ] Translation progress bar (SSE-powered)
- [ ] Download translated PDF button
- [ ] Side-by-side original vs translated preview (stretch)

---

## Phase 3: Performance & Reliability

**Goal:** Make it fast enough and reliable enough to handle real traffic.

- [ ] **Batch inference**: Send multiple texts in a single LLM call instead of sequential
- [ ] **Translation caching**: Redis layer for repeated translations (hash input → cached output)
- [ ] **Streaming responses**: SSE for real-time translation output on long texts
- [ ] **Rate limiting**: IP-based rate limits (middleware or reverse proxy)
- [ ] **Concurrent translation**: `asyncio.gather()` for parallel LLM calls within a batch
- [ ] **Connection pooling**: Tune HTTP client for vLLM connection reuse
- [ ] **Monitoring**: Prometheus metrics (latency, throughput, error rate)
- [ ] **Error recovery**: Retry logic for transient LLM failures

---

## Phase 4: Workflow Features (The Moat)

**Goal:** Translation alone is not a moat. Build workflow features that make Fluently sticky.

### Document Intelligence
- [ ] Auto-summarize translated documents
- [ ] Glossary / terminology management (enforce specific translations)
- [ ] Translation memory (reuse past translations for consistency)

### Integration Layer
- [ ] REST API with API keys for developers
- [ ] Webhook support (translate → callback)
- [ ] Browser extension ("translate this page")
- [ ] Slack integration (translate messages in channels)

### Support Ticket Workflow
- [ ] Language routing: auto-detect ticket language → assign to right team
- [ ] Auto-translate incoming tickets for support agents
- [ ] Auto-summarize translated tickets

---

## Phase 5: Scale & Monetization

- [ ] User accounts and usage tracking
- [ ] Tiered pricing (free tier → paid for volume)
- [ ] Multi-model support (swap in different models for different language pairs)
- [ ] On-prem deployment option for enterprise
- [ ] DOCX / PPTX translation support
- [ ] Batch file translation (upload many → download translated zip)

---

## Ownership

| Area | Owner | Notes |
|------|-------|-------|
| Backend API core | Friend | Translation logic, LLM integration, language detection |
| Frontend | Myko | React app, UX, API client |
| Infrastructure | Myko | Docker, CI/CD, deployment |
| Docs | Shared | Both maintain docs for their areas |
| PDF pipeline | TBD | New capability, decide ownership when starting Phase 2 |
