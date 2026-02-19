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
): Promise<string[]> {
  return request<string[]>("/translate/", {
    method: "POST",
    body: JSON.stringify({
      contents,
      targetLanguageCode,
      ...(sourceLanguageCode && { sourceLanguageCode }),
    }),
  });
}

/**
 * Translate text extracted from an image.
 */
export async function translateImage(
  imageBase64: string,
  targetLanguageCode: string,
  sourceLanguageCode?: string,
): Promise<string> {
  return request<string>("/translate/image", {
    method: "POST",
    body: JSON.stringify({
      image: imageBase64,
      targetLanguageCode,
      ...(sourceLanguageCode && { sourceLanguageCode }),
    }),
  });
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string }> {
  return request<{ status: string }>("/health");
}

export { ApiError };
