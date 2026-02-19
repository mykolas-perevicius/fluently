import { useTranslation } from "../hooks/useTranslation";
import { LanguageSelector } from "./LanguageSelector";

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

  const handleCopy = async () => {
    if (translatedText) {
      await navigator.clipboard.writeText(translatedText);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Language bar */}
      <div className="flex items-end gap-4 mb-4">
        <LanguageSelector
          value={sourceLanguage}
          onChange={setSourceLanguage}
          showAutoDetect
          label="From"
        />

        <button
          onClick={swap}
          disabled={!sourceLanguage}
          className="
            mb-0.5 p-2 rounded-lg
            text-gray-400 hover:text-fluently-600
            hover:bg-fluently-50 dark:hover:bg-gray-800
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-colors
          "
          title="Swap languages"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
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
        />
      </div>

      {/* Translation panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Source panel */}
        <div className="relative">
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder="Type or paste text to translate..."
            className="
              w-full h-56 p-4 rounded-xl resize-none
              bg-white dark:bg-gray-800
              border border-gray-200 dark:border-gray-700
              text-base leading-relaxed
              placeholder:text-gray-400
              focus:outline-none focus:ring-2 focus:ring-fluently-500 focus:border-transparent
            "
          />
          <div className="absolute bottom-3 right-3 text-xs text-gray-400">
            {sourceText.length > 0 && `${sourceText.length} chars`}
          </div>
          {sourceText.length > 0 && (
            <button
              onClick={() => setSourceText("")}
              className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition-colors"
              title="Clear"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
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

        {/* Target panel */}
        <div className="relative">
          <div
            className="
              w-full h-56 p-4 rounded-xl overflow-y-auto
              bg-gray-50 dark:bg-gray-900
              border border-gray-200 dark:border-gray-700
              text-base leading-relaxed
            "
          >
            {isLoading ? (
              <div className="flex items-center gap-2 text-gray-400">
                <div className="w-4 h-4 border-2 border-fluently-500 border-t-transparent rounded-full animate-spin" />
                Translating...
              </div>
            ) : error ? (
              <div className="text-red-500 text-sm">{error}</div>
            ) : translatedText ? (
              <span>{translatedText}</span>
            ) : (
              <span className="text-gray-400">Translation will appear here</span>
            )}
          </div>

          {translatedText && !isLoading && (
            <button
              onClick={handleCopy}
              className="
                absolute bottom-3 right-3
                px-3 py-1 rounded-md text-xs font-medium
                text-fluently-600 hover:bg-fluently-50
                dark:text-fluently-400 dark:hover:bg-gray-800
                transition-colors
              "
              title="Copy translation"
            >
              Copy
            </button>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="mt-4 text-center text-xs text-gray-400">
        {!sourceLanguage && sourceText.length > 0 && !isLoading && (
          <span>Language auto-detected</span>
        )}
      </div>
    </div>
  );
}
