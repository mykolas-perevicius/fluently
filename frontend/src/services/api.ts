/**
 * Fluently API client.
 *
 * In development, Vite proxies /api → http://localhost:8000.
 * In production, set VITE_API_URL to the backend URL.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, text);
  }

  return res.json() as Promise<T>;
}

/**
 * Translate an array of text strings.
 */
export async function translateText(
  contents: string[],
  targetLanguageCode: string,
  sourceLanguageCode?: string,
  signal?: AbortSignal,
): Promise<string[]> {
  return request<string[]>("/translate/", {
    method: "POST",
    signal,
    body: JSON.stringify({
      contents,
      targetLanguageCode,
      ...(sourceLanguageCode && { sourceLanguageCode }),
    }),
  });
}

/**
 * Translate text extracted from an image.
 * Returns translation text and the X-Text-Type header (printed/handwritten/mixed).
 */
export async function translateImage(
  imageBase64: string,
  targetLanguageCode: string,
  sourceLanguageCode?: string,
): Promise<{ text: string; textType: string }> {
  const res = await fetch(`${BASE_URL}/translate/image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image: imageBase64,
      targetLanguageCode,
      ...(sourceLanguageCode && { sourceLanguageCode }),
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, text);
  }

  const text = await res.json() as string;
  const textType = res.headers.get("X-Text-Type") ?? "printed";
  return { text, textType };
}

/**
 * Translate a document by chunking text and sending each chunk through the text endpoint.
 * Calls onProgress after each chunk completes.
 */
export async function translateDocument(
  chunks: string[],
  targetLanguageCode: string,
  sourceLanguageCode?: string,
  onProgress?: (completed: number, total: number) => void,
  signal?: AbortSignal,
): Promise<string[]> {
  const results: string[] = [];

  for (const [i, chunk] of chunks.entries()) {
    if (signal?.aborted) throw new DOMException("Aborted", "AbortError");

    const result = await translateText(
      [chunk],
      targetLanguageCode,
      sourceLanguageCode,
      signal,
    );
    results.push(result[0] ?? "");
    onProgress?.(i + 1, chunks.length);
  }

  return results;
}

/**
 * Translate a PDF document with formatting preservation.
 * Uses the backend's PyMuPDF layout extraction + format renderers.
 */
export async function translateDocumentFormatted(
  file: File,
  targetLanguageCode: string,
  sourceLanguageCode?: string,
  signal?: AbortSignal,
): Promise<{
  plaintext: string;
  markdown: string;
  latex: string;
  pageCount: number;
  blockCount: number;
}> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_language_code", targetLanguageCode);
  if (sourceLanguageCode) {
    formData.append("source_language_code", sourceLanguageCode);
  }

  const res = await fetch(`${BASE_URL}/translate/document`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, text);
  }

  const data = await res.json();
  return {
    plaintext: data.plaintext,
    markdown: data.markdown,
    latex: data.latex,
    pageCount: data.page_count,
    blockCount: data.block_count,
  };
}

/**
 * Detect PII entities in text.
 */
export async function detectPII(
  text: string,
): Promise<{
  entities: Array<{
    type: string;
    value: string;
    start: number;
    end: number;
    confidence: number;
    source: "regex" | "llm";
  }>;
}> {
  return request("/pii/detect", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

/**
 * Redact PII entities from text using the chosen strategy.
 */
export async function redactPII(
  text: string,
  entities: Array<{
    type: string;
    value: string;
    start: number;
    end: number;
    confidence: number;
    source: string;
  }>,
  strategy: "mask" | "asterisk" | "synthetic" = "mask",
): Promise<{ redacted_text: string; redaction_count: number }> {
  return request("/pii/redact", {
    method: "POST",
    body: JSON.stringify({ text, entities, strategy }),
  });
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}

export { ApiError };
