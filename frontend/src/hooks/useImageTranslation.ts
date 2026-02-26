import { useState, useEffect, useCallback, useRef } from "react";
import { translateImage } from "../services/api";

const HANDWRITTEN_MIN_DISPLAY_MS = 6000;

export function useImageTranslation(
  targetLanguage: string,
  sourceLanguage: string | undefined,
) {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [translatedText, setTranslatedText] = useState("");
  const [textType, setTextType] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const delayTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleFileSelect = useCallback((file: File) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
    if (!allowedTypes.includes(file.type)) {
      setError("Unsupported format. Use JPG, PNG, or WEBP.");
      return;
    }
    setImageFile(file);
    setError(null);
    setTranslatedText("");
    setTextType(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setImagePreview(result);
      setImageBase64(result);
    };
    reader.readAsDataURL(file);
  }, []);

  const removeImage = useCallback(() => {
    clearTimeout(delayTimerRef.current);
    setImageFile(null);
    setImagePreview(null);
    setImageBase64(null);
    setTranslatedText("");
    setTextType(null);
    setError(null);
    setIsProcessing(false);
  }, []);

  // Auto-translate when image or languages change
  useEffect(() => {
    if (!imageBase64) return;

    let cancelled = false;
    const startTime = Date.now();
    setIsProcessing(true);
    setError(null);
    setTranslatedText("");
    setTextType(null);

    translateImage(imageBase64, targetLanguage, sourceLanguage)
      .then((result) => {
        if (cancelled) return;

        setTextType(result.textType);

        // For handwritten text, add deliberate delay (2x perceived time)
        if (result.textType === "handwritten") {
          const elapsed = Date.now() - startTime;
          const remaining = Math.max(0, HANDWRITTEN_MIN_DISPLAY_MS - elapsed);

          delayTimerRef.current = setTimeout(() => {
            if (!cancelled) {
              setTranslatedText(result.text);
              setIsProcessing(false);
            }
          }, remaining);
        } else {
          setTranslatedText(result.text);
          setIsProcessing(false);
        }
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Translation failed");
        if (!cancelled) setIsProcessing(false);
      });

    return () => {
      cancelled = true;
      clearTimeout(delayTimerRef.current);
    };
  }, [imageBase64, targetLanguage, sourceLanguage]);

  return {
    imageFile,
    imagePreview,
    translatedText,
    textType,
    isProcessing,
    error,
    handleFileSelect,
    removeImage,
  };
}
