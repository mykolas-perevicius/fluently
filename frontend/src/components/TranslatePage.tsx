import { useState, useRef, useEffect } from "react";
import { useTranslation } from "../hooks/useTranslation";
import { LanguageSelector } from "./LanguageSelector";
import { COMMON_LANGUAGES } from "../types";

const MAX_CHARS = 5000;

type Tab = "text" | "image" | "document";

export function TranslatePage() {
  const {
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
  } = useTranslation();

  const [activeTab, setActiveTab] = useState<Tab>("text");
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.max(160, el.scrollHeight) + "px";
    }
  }, [sourceText]);

  const handleCopy = async () => {
    if (translatedText) {
      await navigator.clipboard.writeText(translatedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const sourceLangName =
    sourceLanguage === undefined
      ? "AUTO-DETECT"
      : (
          COMMON_LANGUAGES.find((l) => l.code === sourceLanguage)?.name ??
          sourceLanguage
        ).toUpperCase();

  const targetLangName = (
    COMMON_LANGUAGES.find((l) => l.code === targetLanguage)?.name ??
    targetLanguage
  ).toUpperCase();

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 flex flex-col gap-4">
      {/* Tab Bar */}
      <div className="glass rounded-2xl p-1.5 flex gap-1 shadow-glass">
        {(
          [
            { id: "text", label: "Text", disabled: false },
            { id: "image", label: "Image", disabled: false },
            { id: "document", label: "Document", disabled: true },
          ] as const
        ).map((tab) => (
          <button
            key={tab.id}
            data-testid={`tab-${tab.id}`}
            disabled={tab.disabled}
            onClick={() => !tab.disabled && setActiveTab(tab.id)}
            className={`
              flex-1 py-2.5 px-4 rounded-xl text-sm font-display font-medium
              transition-all duration-200
              ${
                activeTab === tab.id
                  ? "bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 text-white border border-accent-cyan/20 shadow-glow-cyan"
                  : tab.disabled
                    ? "text-slate-400/40 cursor-not-allowed"
                    : "text-slate-400 hover:text-slate-200 cursor-pointer"
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Language Bar */}
      <div className="flex items-center gap-2 justify-center">
        <LanguageSelector
          value={sourceLanguage}
          onChange={setSourceLanguage}
          showAutoDetect
          label="From"
          variant="source"
          testId="source-language-selector"
        />

        {/* Swap button */}
        <button
          data-testid="swap-languages"
          onClick={swap}
          disabled={!sourceLanguage}
          className="
            w-9 h-9 rounded-full glass flex items-center justify-center
            text-slate-400 hover:text-white
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-all duration-200 hover:bg-white/5 shrink-0
          "
          title="Swap languages"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M7 16V4m0 0L3 8m4-4l4 4" />
            <path d="M17 8v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>

        <LanguageSelector
          value={targetLanguage}
          onChange={(code) => code && setTargetLanguage(code)}
          label="To"
          variant="target"
          testId="target-language-selector"
        />
      </div>

      {/* Translation Card */}
      <div className="glass rounded-3xl shadow-glass overflow-hidden">
        {/* Source half */}
        <div className="relative p-5 min-h-[180px]">
          {/* Source language label */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-display font-medium tracking-[0.15em] text-accent-cyan uppercase">
              {sourceLangName}
            </span>

            {/* Clear button */}
            {sourceText.length > 0 && (
              <button
                onClick={() => setSourceText("")}
                className="text-slate-500 hover:text-slate-300 transition-colors"
                title="Clear"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            )}
          </div>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            data-testid="source-textarea"
            value={sourceText}
            onChange={(e) => {
              if (e.target.value.length <= MAX_CHARS) {
                setSourceText(e.target.value);
              }
            }}
            placeholder="Type or paste text to translate..."
            className="
              w-full bg-transparent resize-none text-[17px] leading-relaxed
              text-white placeholder:text-slate-600
              focus:outline-none min-h-[120px]
            "
          />

          {/* Char count */}
          <div
            data-testid="char-count"
            className="text-right text-[11px] text-slate-400/60 font-display mt-1"
          >
            {sourceText.length}/{MAX_CHARS}
          </div>
        </div>

        {/* Gradient divider */}
        <div className="relative h-px">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          <div className="absolute inset-0 shadow-glow-purple" />
        </div>

        {/* Target half */}
        <div className="relative p-5 min-h-[180px]">
          {/* Target language label */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-display font-medium tracking-[0.15em] text-accent-purple/90 uppercase">
              {targetLangName}
            </span>
          </div>

          {/* Translation output */}
          <div data-testid="translation-output" className="min-h-[120px]">
            {isLoading ? (
              <div
                data-testid="loading-indicator"
                className="flex items-center gap-2.5 text-slate-400"
              >
                <div className="w-4 h-4 border-2 border-accent-purple border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-display">Translating...</span>
              </div>
            ) : error ? (
              <div
                data-testid="error-message"
                className="text-red-400 text-sm"
              >
                {error}
              </div>
            ) : translatedText ? (
              <p className="text-[17px] leading-relaxed text-white">
                {translatedText}
              </p>
            ) : (
              <p className="text-[17px] leading-relaxed text-slate-600">
                Translation will appear here
              </p>
            )}
          </div>

          {/* Copy button */}
          {translatedText && !isLoading && (
            <div className="flex justify-end mt-3">
              <button
                data-testid="copy-button"
                onClick={handleCopy}
                className="
                  flex items-center gap-1.5 px-3.5 py-2 rounded-xl
                  bg-accent-purple/10 text-accent-purple
                  border border-accent-purple/20
                  hover:bg-accent-purple/15 transition-all duration-200
                  text-xs font-display font-medium
                "
                title="Copy translation"
              >
                {copied ? (
                  <>
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    Copied
                  </>
                ) : (
                  <>
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <rect
                        x="9"
                        y="9"
                        width="13"
                        height="13"
                        rx="2"
                        ry="2"
                      />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                    Copy
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
