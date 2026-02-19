import { useState, useEffect, useRef, useCallback } from "react";
import { translateText } from "../services/api";

interface UseTranslationOptions {
  debounceMs?: number;
}

interface UseTranslationReturn {
  sourceText: string;
  setSourceText: (text: string) => void;
  translatedText: string;
  sourceLanguage: string | undefined;
  setSourceLanguage: (lang: string | undefined) => void;
  targetLanguage: string;
  setTargetLanguage: (lang: string) => void;
  isLoading: boolean;
  error: string | null;
  swap: () => void;
}

export function useTranslation(
  options: UseTranslationOptions = {},
): UseTranslationReturn {
  const { debounceMs = 500 } = options;

  const [sourceText, setSourceText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [sourceLanguage, setSourceLanguage] = useState<string | undefined>(
    undefined,
  );
  const [targetLanguage, setTargetLanguage] = useState("es");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const abortRef = useRef<AbortController>(undefined);

  const doTranslate = useCallback(
    async (text: string, source: string | undefined, target: string) => {
      if (!text.trim()) {
        setTranslatedText("");
        setError(null);
        return;
      }

      // Cancel any in-flight request
      abortRef.current?.abort();
      abortRef.current = new AbortController();

      setIsLoading(true);
      setError(null);

      try {
        const result = await translateText([text], target, source);
        setTranslatedText(result[0] ?? "");
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Translation failed");
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  // Debounced translation trigger
  useEffect(() => {
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      doTranslate(sourceText, sourceLanguage, targetLanguage);
    }, debounceMs);

    return () => clearTimeout(timerRef.current);
  }, [sourceText, sourceLanguage, targetLanguage, debounceMs, doTranslate]);

  const swap = useCallback(() => {
    if (!sourceLanguage) return; // can't swap if source is auto-detect

    const prevSource = sourceLanguage;
    const prevTarget = targetLanguage;
    const prevTranslated = translatedText;

    setSourceLanguage(prevTarget);
    setTargetLanguage(prevSource);
    setSourceText(prevTranslated);
    setTranslatedText("");
  }, [sourceLanguage, targetLanguage, translatedText]);

  return {
    sourceText,
    setSourceText,
    translatedText,
    sourceLanguage,
    setSourceLanguage,
    targetLanguage,
    setTargetLanguage,
    isLoading,
    error,
    swap,
  };
}
