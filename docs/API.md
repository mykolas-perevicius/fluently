# Fluently API Reference

> Auto-generated OpenAPI docs available at `http://localhost:8000/docs` when the backend is running.
> This document provides a human-readable summary.

---

## Base URL

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000` |
| Frontend proxy | `/api` (Vite proxies to backend) |
| Production | TBD |

---

## Endpoints

### `GET /health`

Liveness check.

**Response:** `200 OK`
```json
{ "status": "ok" }
```

---

### `POST /translate/`

Translate an array of text strings.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contents` | `string[]` | Yes | 1–50 text strings to translate |
| `targetLanguageCode` | `string` | Yes | ISO 639-1 target language code |
| `sourceLanguageCode` | `string` | No | ISO 639-1 source code. Auto-detected if omitted. |

**Example:**
```json
{
  "contents": ["Hello, how are you?"],
  "targetLanguageCode": "es"
}
```

**Response:** `200 OK` — array of translated strings
```json
["Hola, ¿cómo estás?"]
```

**Errors:**
- `400` — Unsupported language code
- `422` — Validation error
- `500` — Translation failed

---

### `POST /translate/image`

Extract and translate text from an image.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | `string` (base64) | Yes | Base64-encoded image data. Max 5MB. PNG or JPEG. |
| `targetLanguageCode` | `string` | Yes | ISO 639-1 target language code |
| `sourceLanguageCode` | `string` | No | ISO 639-1 source code. Auto-detected if omitted. |

**Example:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgo...",
  "targetLanguageCode": "es"
}
```

**Response:** `200 OK` — translated text as a string
```json
"Texto traducido de la imagen"
```

**Errors:**
- `400` — Unsupported language code
- `422` — Invalid image format or encoding
- `500` — Processing failed

---

## Supported Languages

The API supports 600+ ISO 639-1 language codes and regional variants. The full enum is defined in `backend/src/utils/language.py`.

**Common codes:** `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `ru`, `zh`, `ja`, `ko`, `ar`, `hi`, `tr`, `pl`, `uk`, `vi`, `th`, `sv`

---

## Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` for most endpoints; `multipart/form-data` for `/translate/document` |
| `Accept-Language` | No | RFC 7231 header; used as fallback for source language detection |

---

### `POST /translate/document`

Translate a PDF document with layout-aware formatting. Extracts structured blocks (headings, paragraphs, lists, tables) via PyMuPDF, translates all blocks, and returns the result in three formats.

**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | `file` | Yes | PDF file to translate. Max 10MB, max 100 pages. |
| `target_language_code` | `string` | Yes | ISO 639-1 target language code |
| `source_language_code` | `string` | No | ISO 639-1 source code. Auto-detected if omitted. |

**Example:**
```bash
curl -X POST http://localhost:8000/translate/document \
  -F file=@document.pdf \
  -F target_language_code=es
```

**Response:** `200 OK`
```json
{
  "plaintext": "INTRODUCTION\n============\n...",
  "markdown": "# Introduction\n\n...",
  "latex": "\\documentclass{article}\n...",
  "page_count": 5,
  "block_count": 42
}
```

**Errors:**
- `400` — Not a PDF, file too large, too many pages, no text found, or unsupported language
- `500` — Processing failed

---

### `POST /pii/detect`

Detect personally identifiable information in text using a hybrid approach: regex patterns for structured PII (emails, phones, SSNs, credit cards, IP addresses) and LLM for contextual PII (names, addresses, organizations).

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | Yes | Text to scan for PII. Max 50,000 characters. |

**Example:**
```json
{
  "text": "Contact John Smith at john@example.com or 555-123-4567."
}
```

**Response:** `200 OK`
```json
{
  "entities": [
    { "type": "PERSON_NAME", "value": "John Smith", "start": 8, "end": 18, "confidence": 0.85, "source": "llm" },
    { "type": "EMAIL", "value": "john@example.com", "start": 22, "end": 38, "confidence": 0.95, "source": "regex" },
    { "type": "PHONE", "value": "555-123-4567", "start": 42, "end": 54, "confidence": 0.95, "source": "regex" }
  ]
}
```

---

### `POST /pii/redact`

Redact specified PII entities from text using a chosen strategy.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | Yes | Original text containing PII |
| `entities` | `PIIEntity[]` | Yes | Entities to redact (from `/pii/detect` response) |
| `strategy` | `string` | No | `"mask"` (default), `"asterisk"`, or `"synthetic"` |

**Response:** `200 OK`
```json
{
  "redacted_text": "Contact [PERSON_NAME] at [EMAIL] or [PHONE].",
  "redaction_count": 3
}
```

---

## Future Endpoints (planned)

| Endpoint | Description |
|----------|-------------|
| `POST /translate/stream` | SSE streaming for long translations |
| `GET /languages` | List supported languages |
