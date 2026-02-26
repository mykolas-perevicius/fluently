import { useState, useCallback, useRef, useMemo } from "react";
import { extractDocument, type ExtractionResult } from "../utils/documentExtractor";
import { translateDocument, translateDocumentFormatted } from "../services/api";
import type { OutputFormat, FormattedDocumentOutput } from "../types";

const CHUNK_SIZE = 4000;

function chunkText(text: string): string[] {
  if (text.length <= CHUNK_SIZE) return [text];

  const chunks: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= CHUNK_SIZE) {
      chunks.push(remaining);
      break;
    }

    // Find the last sentence boundary within the chunk size
    const slice = remaining.slice(0, CHUNK_SIZE);
    const lastSentence = Math.max(
      slice.lastIndexOf(". "),
      slice.lastIndexOf("! "),
      slice.lastIndexOf("? "),
      slice.lastIndexOf(".\n"),
      slice.lastIndexOf("!\n"),
      slice.lastIndexOf("?\n"),
    );

    const splitAt = lastSentence > CHUNK_SIZE * 0.3 ? lastSentence + 1 : CHUNK_SIZE;
    chunks.push(remaining.slice(0, splitAt).trim());
    remaining = remaining.slice(splitAt).trim();
  }

  return chunks.filter((c) => c.length > 0);
}

export interface DocumentTranslationState {
  file: File | null;
  extraction: ExtractionResult | null;
  translatedText: string;
  isExtracting: boolean;
  isTranslating: boolean;
  error: string | null;
  progress: { completed: number; total: number } | null;
  handleFileSelect: (file: File) => void;
  removeFile: () => void;
  translate: () => void;
  // Formatted output (PDF only)
  isPdf: boolean;
  formattedOutput: FormattedDocumentOutput | null;
  activeFormat: OutputFormat;
  setActiveFormat: (format: OutputFormat) => void;
  translateFormatted: () => void;
}

export function useDocumentTranslation(
  targetLanguage: string,
  sourceLanguage: string | undefined,
): DocumentTranslationState {
  const [file, setFile] = useState<File | null>(null);
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null);
  const [translatedText, setTranslatedText] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<{ completed: number; total: number } | null>(null);
  const [formattedOutput, setFormattedOutput] = useState<FormattedDocumentOutput | null>(null);
  const [activeFormat, setActiveFormat] = useState<OutputFormat>("plaintext");
  const abortRef = useRef<AbortController | undefined>(undefined);

  const isPdf = useMemo(
    () => file?.type === "application/pdf" || (file?.name?.toLowerCase().endsWith(".pdf") ?? false),
    [file],
  );

  const handleFileSelect = useCallback((f: File) => {
    // Cancel any in-flight translation
    abortRef.current?.abort();

    setFile(f);
    setTranslatedText("");
    setFormattedOutput(null);
    setActiveFormat("plaintext");
    setError(null);
    setProgress(null);
    setIsExtracting(true);

    extractDocument(f)
      .then((result) => {
        setExtraction(result);
        if (!result.supported) {
          setError(`${result.formatName} format is not yet supported. Coming soon!`);
        } else if (!result.text.trim()) {
          setError("No extractable text found in this document.");
        }
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to extract text");
        setExtraction(null);
      })
      .finally(() => setIsExtracting(false));
  }, []);

  const removeFile = useCallback(() => {
    abortRef.current?.abort();
    setFile(null);
    setExtraction(null);
    setTranslatedText("");
    setFormattedOutput(null);
    setActiveFormat("plaintext");
    setError(null);
    setProgress(null);
    setIsExtracting(false);
    setIsTranslating(false);
  }, []);

  const translate = useCallback(() => {
    if (!extraction?.text?.trim()) return;

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    const chunks = chunkText(extraction.text);
    setIsTranslating(true);
    setError(null);
    setTranslatedText("");
    setFormattedOutput(null);
    setProgress({ completed: 0, total: chunks.length });

    translateDocument(
      chunks,
      targetLanguage,
      sourceLanguage,
      (completed, total) => setProgress({ completed, total }),
      abortRef.current.signal,
    )
      .then((results) => {
        setTranslatedText(results.join("\n\n"));
      })
      .catch((err) => {
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Translation failed");
      })
      .finally(() => {
        setIsTranslating(false);
      });
  }, [extraction, targetLanguage, sourceLanguage]);

  const translateFormatted = useCallback(() => {
    if (!file || !isPdf) return;

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setIsTranslating(true);
    setError(null);
    setTranslatedText("");
    setFormattedOutput(null);
    setProgress(null);

    translateDocumentFormatted(
      file,
      targetLanguage,
      sourceLanguage,
      abortRef.current.signal,
    )
      .then((result) => {
        setFormattedOutput(result);
        // Set plaintext as fallback for backward compat
        setTranslatedText(result.plaintext);
      })
      .catch((err) => {
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Formatted translation failed");
      })
      .finally(() => {
        setIsTranslating(false);
      });
  }, [file, isPdf, targetLanguage, sourceLanguage]);

  return {
    file,
    extraction,
    translatedText,
    isExtracting,
    isTranslating,
    error,
    progress,
    handleFileSelect,
    removeFile,
    translate,
    isPdf,
    formattedOutput,
    activeFormat,
    setActiveFormat,
    translateFormatted,
  };
}
