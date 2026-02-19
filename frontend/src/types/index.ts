/**
 * Common languages shown in the quick-select dropdown.
 * The full list lives in the backend's LanguageCode enum (600+ codes).
 * We expose a curated set for the UI.
 */
export interface Language {
  code: string;
  name: string;
}

/**
 * The curated set of languages shown in the UI dropdowns.
 * This covers the most commonly requested translation pairs.
 */
export const COMMON_LANGUAGES: Language[] = [
  { code: "en", name: "English" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "nl", name: "Dutch" },
  { code: "ru", name: "Russian" },
  { code: "zh", name: "Chinese" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "ar", name: "Arabic" },
  { code: "hi", name: "Hindi" },
  { code: "tr", name: "Turkish" },
  { code: "pl", name: "Polish" },
  { code: "uk", name: "Ukrainian" },
  { code: "vi", name: "Vietnamese" },
  { code: "th", name: "Thai" },
  { code: "sv", name: "Swedish" },
  { code: "da", name: "Danish" },
  { code: "fi", name: "Finnish" },
  { code: "no", name: "Norwegian" },
  { code: "cs", name: "Czech" },
  { code: "ro", name: "Romanian" },
  { code: "hu", name: "Hungarian" },
  { code: "el", name: "Greek" },
  { code: "he", name: "Hebrew" },
  { code: "id", name: "Indonesian" },
  { code: "ms", name: "Malay" },
  { code: "tl", name: "Tagalog" },
];

export interface TranslationRequest {
  contents: string[];
  targetLanguageCode: string;
  sourceLanguageCode?: string;
}

export interface ImageTranslationRequest {
  image: string; // base64
  targetLanguageCode: string;
  sourceLanguageCode?: string;
}
