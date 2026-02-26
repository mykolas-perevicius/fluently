import { useState, useRef, useCallback } from "react";
import { ALL_EXTENSIONS } from "../utils/documentExtractor";
import type { DocumentTranslationState } from "../hooks/useDocumentTranslation";
import { usePIIDetection } from "../hooks/usePIIDetection";
import type { OutputFormat } from "../types";

const ACCEPT = ALL_EXTENSIONS.join(",");

const FORMAT_BADGES = [
  { label: "PDF", supported: true },
  { label: "TXT", supported: true },
  { label: "MD", supported: true },
  { label: "CSV", supported: true },
  { label: "HTML", supported: true },
  { label: "DOCX", supported: false },
  { label: "XLSX", supported: false },
];

const FORMAT_TABS: { id: OutputFormat; label: string; ext: string }[] = [
  { id: "plaintext", label: "Plain", ext: ".txt" },
  { id: "markdown", label: "Markdown", ext: ".md" },
  { id: "latex", label: "LaTeX", ext: ".tex" },
];

const STRATEGY_OPTIONS = [
  { value: "mask" as const, label: "Mask ([EMAIL])" },
  { value: "asterisk" as const, label: "Asterisk (****)" },
  { value: "synthetic" as const, label: "Synthetic (fake data)" },
];

function downloadFile(content: string, filename: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function DocumentTranslatePanel(props: DocumentTranslationState) {
  const {
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
  } = props;

  const pii = usePIIDetection();

  const [isDragging, setIsDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) {
        pii.reset();
        handleFileSelect(f);
      }
    },
    [handleFileSelect, pii],
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) {
        pii.reset();
        handleFileSelect(f);
      }
    },
    [handleFileSelect, pii],
  );

  const handleCopy = async () => {
    const text = formattedOutput
      ? formattedOutput[activeFormat === "latex" ? "latex" : activeFormat === "markdown" ? "markdown" : "plaintext"]
      : translatedText;
    if (text) {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = (format: OutputFormat) => {
    if (!formattedOutput) return;
    const tab = FORMAT_TABS.find((t) => t.id === format);
    const baseName = file?.name?.replace(/\.pdf$/i, "") ?? "document";
    const content =
      format === "plaintext"
        ? formattedOutput.plaintext
        : format === "markdown"
          ? formattedOutput.markdown
          : formattedOutput.latex;
    downloadFile(content, `${baseName}-translated${tab?.ext ?? ".txt"}`);
  };

  const handleTranslate = async () => {
    if (pii.isEnabled && extraction?.text) {
      await pii.detect(extraction.text);
      // After detection, user reviews entities, then clicks translate again
      return;
    }
    translate();
  };

  const handleTranslateWithPII = async () => {
    // User has reviewed PII entities and confirmed — redact then translate
    if (pii.selectedEntities.length > 0 && extraction?.text) {
      await pii.redact(extraction.text);
    }
    translate();
  };

  const isSupported = extraction?.supported ?? true;
  const hasText = extraction?.text?.trim();
  const isProcessing = isExtracting || isTranslating;
  const progressPct = progress ? Math.round((progress.completed / progress.total) * 100) : 0;
  const showPIIReview = pii.isEnabled && pii.entities.length > 0 && !isTranslating && !translatedText && !formattedOutput;

  return (
    <div className="flex flex-col gap-4">
      {/* Title */}
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-display font-bold tracking-tight text-white">
          Document Translation
        </h2>
        <p className="text-sm text-slate-400">
          {isExtracting
            ? "Extracting text from your document..."
            : isTranslating
              ? `Translating... ${progress ? `${progressPct}%` : ""}`
              : pii.isDetecting
                ? "Scanning for PII..."
                : "Upload a document to extract and translate its text."}
        </p>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Upload / File info */}
        {!file ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              relative flex flex-col items-center justify-center gap-6
              p-8 rounded-2xl cursor-pointer transition-all duration-200
              bg-[#111827] border-2 border-dashed min-h-[300px]
              ${isDragging
                ? "border-accent-cyan bg-accent-cyan/5"
                : "border-[#374151] hover:border-[#4B5563]"
              }
            `}
          >
            {/* Upload icon */}
            <div className="p-6 rounded-full bg-accent-purple/20">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent-purple">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="12" y1="18" x2="12" y2="12" />
                <polyline points="9 15 12 12 15 15" />
              </svg>
            </div>

            <div className="flex flex-col items-center gap-2">
              <span className="text-lg font-bold text-white">Upload Document</span>
              <span className="text-sm text-slate-400 text-center">
                Drop a document here or click to upload
              </span>
            </div>

            {/* Format badges */}
            <div className="flex flex-wrap gap-2 pt-2 justify-center">
              {FORMAT_BADGES.map((fmt) => (
                <span
                  key={fmt.label}
                  className={`px-2 py-1 text-xs font-medium rounded-lg border ${
                    fmt.supported
                      ? "text-slate-300 bg-[#1F2937] border-[#374151]"
                      : "text-slate-500 bg-[#1F2937]/50 border-[#374151]/50"
                  }`}
                >
                  {fmt.label}
                  {!fmt.supported && <span className="text-[10px] ml-1 opacity-60">soon</span>}
                </span>
              ))}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept={ACCEPT}
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        ) : (
          <div className="relative rounded-2xl bg-[#111827] border border-[#374151] p-6 min-h-[300px] flex flex-col">
            {/* File info header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-accent-purple/10 border border-accent-purple/20">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent-purple">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-white truncate max-w-[200px]">{file.name}</p>
                  <p className="text-xs text-slate-500">
                    {extraction?.formatName ?? "..."} &middot; {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={() => { pii.reset(); removeFile(); }}
                className="w-7 h-7 rounded-full bg-[#1F2937] flex items-center justify-center text-slate-400 hover:text-white hover:bg-[#374151] transition-colors"
              >
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                  <path d="M1 1l8 8M9 1l-8 8" />
                </svg>
              </button>
            </div>

            {/* Extracted text preview */}
            {hasText && isSupported && (
              <div className="flex-1 overflow-auto rounded-xl bg-[#0D1117] border border-[#1F2937] p-4 mb-4">
                <p className="text-xs text-slate-500 mb-2 font-display font-medium tracking-wider uppercase">
                  Extracted Text Preview
                </p>
                <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap line-clamp-[12]">
                  {extraction!.text.slice(0, 1000)}
                  {extraction!.text.length > 1000 && "..."}
                </p>
              </div>
            )}

            {/* PII Toggle */}
            {hasText && isSupported && !isProcessing && !translatedText && !formattedOutput && (
              <label className="flex items-center gap-3 mb-3 cursor-pointer select-none">
                <div
                  onClick={() => { pii.setIsEnabled(!pii.isEnabled); pii.reset(); }}
                  className={`
                    relative w-10 h-5 rounded-full transition-colors duration-200
                    ${pii.isEnabled ? "bg-accent-cyan" : "bg-[#374151]"}
                  `}
                >
                  <div
                    className={`
                      absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200
                      ${pii.isEnabled ? "translate-x-5" : "translate-x-0.5"}
                    `}
                  />
                </div>
                <span className="text-sm text-slate-300 font-display">
                  Scan for PII before translating
                </span>
              </label>
            )}

            {/* PII Entity Review */}
            {showPIIReview && (
              <div className="rounded-xl bg-[#0D1117] border border-amber-500/20 p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-xs font-display font-medium tracking-wider uppercase text-amber-400">
                    PII Detected ({pii.entities.length})
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={pii.selectAll}
                      className="text-[10px] px-2 py-0.5 rounded bg-[#1F2937] text-slate-400 hover:text-white transition-colors"
                    >
                      All
                    </button>
                    <button
                      onClick={pii.deselectAll}
                      className="text-[10px] px-2 py-0.5 rounded bg-[#1F2937] text-slate-400 hover:text-white transition-colors"
                    >
                      None
                    </button>
                  </div>
                </div>

                <div className="max-h-[120px] overflow-y-auto space-y-1.5 mb-3">
                  {pii.entities.map((entity, i) => (
                    <label key={i} className="flex items-center gap-2 cursor-pointer text-sm">
                      <input
                        type="checkbox"
                        checked={pii.selectedEntities.includes(entity)}
                        onChange={() => pii.toggleEntity(i)}
                        className="rounded border-[#374151] bg-[#1F2937] text-accent-cyan focus:ring-accent-cyan/50"
                      />
                      <span className="px-1.5 py-0.5 text-[10px] rounded bg-amber-500/10 text-amber-400 font-medium uppercase">
                        {entity.type}
                      </span>
                      <span className="text-slate-300 truncate">{entity.value}</span>
                      <span className="text-[10px] text-slate-500 ml-auto">
                        {Math.round(entity.confidence * 100)}%
                      </span>
                    </label>
                  ))}
                </div>

                {/* Strategy selector */}
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs text-slate-400">Redaction:</span>
                  <select
                    value={pii.strategy}
                    onChange={(e) => pii.setStrategy(e.target.value as typeof pii.strategy)}
                    className="text-xs bg-[#1F2937] border border-[#374151] text-slate-300 rounded-lg px-2 py-1 focus:outline-none focus:border-accent-cyan/50"
                  >
                    {STRATEGY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleTranslateWithPII}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-white text-sm font-display font-semibold hover:brightness-110 transition-all"
                >
                  Redact & Translate
                </button>
              </div>
            )}

            {/* Translate buttons */}
            {hasText && isSupported && !isProcessing && !translatedText && !formattedOutput && !showPIIReview && (
              <div className="flex flex-col gap-2">
                {/* Standard translate */}
                <button
                  onClick={pii.isEnabled && pii.entities.length === 0 ? handleTranslate : translate}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-accent-cyan to-accent-purple text-white text-sm font-display font-semibold hover:brightness-110 transition-all"
                >
                  {pii.isEnabled && pii.entities.length === 0 ? "Scan PII & Translate" : "Translate Document"}
                </button>

                {/* Formatted translate (PDF only) */}
                {isPdf && (
                  <button
                    onClick={translateFormatted}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white text-sm font-display font-semibold hover:brightness-110 transition-all flex items-center justify-center gap-2"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                    Translate with Formatting
                  </button>
                )}
              </div>
            )}

            {/* Progress bar */}
            {isTranslating && progress && (
              <div className="mt-auto">
                <div className="flex justify-between text-xs text-slate-400 mb-2">
                  <span>Translating...</span>
                  <span>{progress.completed}/{progress.total} chunks</span>
                </div>
                <div className="h-2 rounded-full bg-[#1F2937] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-accent-cyan to-accent-purple transition-all duration-300"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              </div>
            )}

            {/* Formatted translation in progress (no chunk progress) */}
            {isTranslating && !progress && (
              <div className="flex items-center gap-2 text-slate-400 mt-auto">
                <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-display">Extracting layout & translating...</span>
              </div>
            )}

            {/* Extracting spinner */}
            {isExtracting && (
              <div className="flex items-center gap-2 text-slate-400 mt-auto">
                <div className="w-4 h-4 border-2 border-accent-purple border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-display">Extracting text...</span>
              </div>
            )}

            {/* PII detecting spinner */}
            {pii.isDetecting && (
              <div className="flex items-center gap-2 text-slate-400 mt-auto">
                <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm font-display">Scanning for PII...</span>
              </div>
            )}
          </div>
        )}

        {/* Right: Translation output */}
        <div className="relative rounded-2xl bg-[#111827] border border-[#374151] p-8 flex flex-col items-center justify-center overflow-hidden min-h-[300px]">
          {isProcessing && !translatedText && !formattedOutput ? (
            <>
              <div className="w-16 h-16 mb-6">
                <svg className="animate-spin" width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <circle cx="32" cy="32" r="26" stroke="#1F2937" strokeWidth="6" />
                  <circle cx="32" cy="32" r="26" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeDasharray="120" strokeDashoffset="80" className="text-accent-purple" />
                </svg>
              </div>
              <span className="text-lg font-bold text-white text-center">
                {isExtracting ? "Extracting text..." : "Translating document..."}
              </span>
              <span className="text-sm text-slate-400 text-center mt-2">
                {isExtracting
                  ? "Reading and parsing your document."
                  : progress
                    ? `Processing chunk ${progress.completed} of ${progress.total}`
                    : "Extracting layout and translating blocks..."}
              </span>
              <div className="absolute w-64 h-64 rounded-full bg-accent-purple/10 blur-[100px] pointer-events-none" />
            </>
          ) : error ? (
            <div className="text-red-400 text-sm text-center">{error}</div>
          ) : formattedOutput ? (
            /* ── Formatted output with tabs ─────────────────────── */
            <div className="w-full flex flex-col gap-3 self-start items-start">
              {/* Format tab bar */}
              <div className="w-full flex items-center justify-between">
                <div className="glass rounded-xl p-1 flex gap-0.5">
                  {FORMAT_TABS.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveFormat(tab.id)}
                      className={`
                        px-3 py-1.5 rounded-lg text-xs font-display font-medium transition-all duration-200
                        ${activeFormat === tab.id
                          ? "bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 text-white border border-accent-cyan/20 shadow-glow-cyan"
                          : "text-slate-400 hover:text-slate-200"
                        }
                      `}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Download button */}
                <button
                  onClick={() => handleDownload(activeFormat)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 hover:bg-accent-cyan/15 transition-all duration-200 text-xs font-display font-medium"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  {FORMAT_TABS.find((t) => t.id === activeFormat)?.ext}
                </button>
              </div>

              {/* Content area */}
              <div className="w-full max-h-[400px] overflow-auto rounded-xl bg-[#0D1117] border border-[#1F2937] p-4">
                <pre className="text-[13px] leading-relaxed text-white whitespace-pre-wrap font-mono">
                  {activeFormat === "plaintext"
                    ? formattedOutput.plaintext
                    : activeFormat === "markdown"
                      ? formattedOutput.markdown
                      : formattedOutput.latex}
                </pre>
              </div>

              {/* Footer: stats + copy */}
              <div className="flex items-center justify-between w-full">
                <span className="text-[11px] text-slate-500">
                  {formattedOutput.pageCount} page{formattedOutput.pageCount !== 1 ? "s" : ""} &middot; {formattedOutput.blockCount} blocks
                </span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-accent-purple/10 text-accent-purple border border-accent-purple/20 hover:bg-accent-purple/15 transition-all duration-200 text-xs font-display font-medium"
                >
                  {copied ? (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Copied
                    </>
                  ) : (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : translatedText ? (
            /* ── Plain text output (existing flow) ───────────────── */
            <div className="w-full flex flex-col gap-4 self-start items-start">
              <span className="text-[11px] font-display font-medium tracking-[0.15em] text-accent-purple uppercase">
                TRANSLATED DOCUMENT
              </span>
              <div className="w-full max-h-[400px] overflow-auto">
                <p className="text-[15px] leading-relaxed text-white whitespace-pre-wrap">
                  {translatedText}
                </p>
              </div>
              <div className="flex justify-end w-full mt-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-accent-purple/10 text-accent-purple border border-accent-purple/20 hover:bg-accent-purple/15 transition-all duration-200 text-xs font-display font-medium"
                >
                  {copied ? (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Copied
                    </>
                  ) : (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="w-16 h-16 mb-6 rounded-full bg-[#1F2937] flex items-center justify-center">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4B5563" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              </div>
              <span className="text-sm text-slate-600 text-center">
                Translation will appear here
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
