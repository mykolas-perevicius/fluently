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
| `Content-Type` | Yes | Must be `application/json` |
| `Accept-Language` | No | RFC 7231 header; used as fallback for source language detection |

---

## Future Endpoints (planned)

| Endpoint | Description |
|----------|-------------|
| `POST /translate/document` | Translate PDF/DOCX files |
| `POST /translate/stream` | SSE streaming for long translations |
| `GET /languages` | List supported languages |
