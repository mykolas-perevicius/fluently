import { useState, useRef, useCallback } from "react";

interface ImageTranslatePanelProps {
  imageFile: File | null;
  imagePreview: string | null;
  translatedText: string;
  textType: string | null;
  isProcessing: boolean;
  error: string | null;
  handleFileSelect: (file: File) => void;
  removeImage: () => void;
}

function TextTypeBadge({ type }: { type: string }) {
  const config = {
    printed: { label: "Printed Text", className: "bg-accent-cyan/10 text-accent-cyan border-accent-cyan/20" },
    handwritten: { label: "Handwritten", className: "bg-accent-purple/10 text-accent-purple border-accent-purple/20" },
    mixed: { label: "Mixed", className: "bg-gradient-to-r from-accent-cyan/10 to-accent-purple/10 text-white border-accent-cyan/20" },
  }[type] ?? { label: type, className: "bg-slate-500/10 text-slate-400 border-slate-500/20" };

  return (
    <span className={`inline-flex px-2.5 py-1 rounded-lg text-xs font-display font-medium border ${config.className}`}>
      {config.label}
    </span>
  );
}

export function ImageTranslatePanel({
  imageFile,
  imagePreview,
  translatedText,
  textType,
  isProcessing,
  error,
  handleFileSelect,
  removeImage,
}: ImageTranslatePanelProps) {
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
      const file = e.dataTransfer.files[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect],
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect],
  );

  const handleCopy = async () => {
    if (translatedText) {
      await navigator.clipboard.writeText(translatedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Title */}
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-display font-bold tracking-tight text-white">
          Image Translation
        </h2>
        <p className="text-sm text-slate-400">
          {isProcessing
            ? "Processing your image..."
            : "Upload an image to detect and translate text instantly."}
        </p>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Upload / Preview */}
        {!imagePreview ? (
          <div
            data-testid="image-upload-zone"
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              relative flex flex-col items-center justify-center gap-6
              p-8 rounded-2xl cursor-pointer transition-all duration-200
              bg-[#111827] border-2 border-dashed min-h-[300px]
              ${
                isDragging
                  ? "border-accent-cyan bg-accent-cyan/5"
                  : "border-[#374151] hover:border-[#4B5563]"
              }
            `}
          >
            {/* Upload icon in blue circle */}
            <div className="p-6 rounded-full bg-accent-cyan/20">
              <svg
                width="32"
                height="24"
                viewBox="0 0 24 18"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-accent-cyan"
              >
                <path d="M4 14.5C2 13.5 1 11.5 1 9a6 6 0 0 1 6-6c.7-1.7 2.2-3 4-3 2.5 0 4.5 1.8 4.9 4.2A5 5 0 0 1 19 9c0 2-1 3.5-2.5 4.5" />
                <path d="M12 12v-6" />
                <path d="M9 9l3-3 3 3" />
              </svg>
            </div>

            {/* Text */}
            <div className="flex flex-col items-center gap-2">
              <span className="text-lg font-bold text-white">
                Upload Image
              </span>
              <span className="text-sm text-slate-400 text-center">
                Drop an image here or click to upload
              </span>
            </div>

            {/* Format badges */}
            <div className="flex gap-2 pt-2">
              {["JPG", "PNG", "WEBP"].map((fmt) => (
                <span
                  key={fmt}
                  className="px-2 py-1 text-xs font-medium text-slate-400 bg-[#1F2937] border border-[#374151] rounded-lg"
                >
                  {fmt}
                </span>
              ))}
            </div>

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        ) : (
          <div
            data-testid="image-preview"
            className="relative rounded-2xl bg-[#111827] border border-[#374151] p-4 min-h-[300px]"
          >
            <div className="relative w-full h-full rounded-lg bg-[#1F2937] overflow-hidden min-h-[268px]">
              <img
                src={imagePreview}
                alt="Uploaded image"
                className="w-full h-full object-contain rounded-lg"
                style={{ filter: isProcessing ? "blur(1px)" : "none" }}
              />

              {/* Filename overlay */}
              <div className="absolute bottom-4 left-4 px-2 py-1 rounded bg-black/60 backdrop-blur-sm">
                <span className="text-xs text-white">{imageFile?.name}</span>
              </div>

              {/* Remove button */}
              <button
                data-testid="remove-image"
                onClick={removeImage}
                className="absolute top-4 right-4 w-7 h-7 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white hover:bg-black/70 transition-colors"
              >
                <svg
                  width="10"
                  height="10"
                  viewBox="0 0 10 10"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                >
                  <path d="M1 1l8 8M9 1l-8 8" />
                </svg>
              </button>
            </div>

            {/* Text type badge */}
            {textType && (
              <div className="mt-3 flex justify-center">
                <TextTypeBadge type={textType} />
              </div>
            )}
          </div>
        )}

        {/* Right: Processing / Results */}
        <div
          data-testid="image-result-panel"
          className="relative rounded-2xl bg-[#111827] border border-[#374151] p-8 flex flex-col items-center justify-center overflow-hidden min-h-[300px]"
        >
          {isProcessing ? (
            <>
              {/* Spinner */}
              <div className="w-16 h-16 mb-6">
                <svg
                  className="animate-spin"
                  width="64"
                  height="64"
                  viewBox="0 0 64 64"
                  fill="none"
                >
                  <circle
                    cx="32"
                    cy="32"
                    r="26"
                    stroke="#1F2937"
                    strokeWidth="6"
                  />
                  <circle
                    cx="32"
                    cy="32"
                    r="26"
                    stroke="currentColor"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeDasharray="120"
                    strokeDashoffset="80"
                    className="text-accent-cyan"
                  />
                </svg>
              </div>
              <span className="text-lg font-bold text-white text-center">
                {textType === "handwritten"
                  ? "Recognizing handwriting..."
                  : "Extracting and translating text..."}
              </span>
              <span className="text-sm text-slate-400 text-center mt-2">
                {textType === "handwritten"
                  ? "Carefully reading handwritten text. This takes a moment."
                  : "We are processing your image to provide the best translation."}
              </span>
              {/* Decorative glow */}
              <div className="absolute w-64 h-64 rounded-full bg-accent-cyan/10 blur-[100px] pointer-events-none" />
            </>
          ) : error ? (
            <div
              data-testid="image-error"
              className="text-red-400 text-sm text-center"
            >
              {error}
            </div>
          ) : translatedText ? (
            <div className="w-full flex flex-col gap-4 self-start items-start">
              <span className="text-[11px] font-display font-medium tracking-[0.15em] text-accent-cyan uppercase">
                TRANSLATED TEXT
              </span>
              <p
                data-testid="image-translation-output"
                className="text-[17px] leading-relaxed text-white whitespace-pre-wrap"
              >
                {translatedText}
              </p>
              <div className="flex justify-end w-full mt-2">
                <button
                  data-testid="image-copy-button"
                  onClick={handleCopy}
                  className="
                    flex items-center gap-1.5 px-3.5 py-2 rounded-xl
                    bg-accent-cyan/10 text-accent-cyan
                    border border-accent-cyan/20
                    hover:bg-accent-cyan/15 transition-all duration-200
                    text-xs font-display font-medium
                  "
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
            </div>
          ) : (
            <>
              <div className="w-16 h-16 mb-6 rounded-full bg-[#1F2937] flex items-center justify-center">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#4B5563"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M5 8l6 6" />
                  <path d="M4 14l6-6 2-3" />
                  <path d="M2 5h12" />
                  <path d="M7 2h1" />
                  <path d="M22 22l-5-10-5 10" />
                  <path d="M14 18h6" />
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
