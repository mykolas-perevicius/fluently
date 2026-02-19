import { useState, useRef, useEffect } from "react";
import { COMMON_LANGUAGES } from "../types";

interface LanguageSelectorProps {
  value: string | undefined;
  onChange: (code: string | undefined) => void;
  showAutoDetect?: boolean;
  label: string;
  variant?: "source" | "target";
  testId?: string;
}

export function LanguageSelector({
  value,
  onChange,
  showAutoDetect = false,
  variant = "source",
  testId,
}: LanguageSelectorProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // Close on click outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setSearch("");
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClick);
      return () => document.removeEventListener("mousedown", handleClick);
    }
  }, [open]);

  // Focus search when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => searchRef.current?.focus(), 0);
    }
  }, [open]);

  const selectedName =
    value === undefined
      ? "Auto-detect"
      : COMMON_LANGUAGES.find((l) => l.code === value)?.name ?? value;

  const filtered = COMMON_LANGUAGES.filter((l) =>
    l.name.toLowerCase().includes(search.toLowerCase()),
  );

  const isCyan = variant === "target";

  return (
    <div ref={ref} className="relative" data-testid={testId}>
      {/* Pill trigger */}
      <button
        onClick={() => setOpen(!open)}
        className={`
          flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-display font-medium
          transition-all duration-200 cursor-pointer
          ${
            isCyan
              ? "bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 shadow-glow-cyan hover:bg-accent-cyan/15"
              : "glass text-slate-300 hover:text-white"
          }
        `}
      >
        <span className="truncate max-w-[120px]">{selectedName}</span>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`shrink-0 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute top-full mt-2 left-0 z-50 w-56 glass-strong rounded-2xl shadow-glass overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
          {/* Search */}
          <div className="p-2">
            <input
              ref={searchRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search languages..."
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-glass-border text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-accent-cyan/30"
            />
          </div>

          {/* Options */}
          <div className="max-h-60 overflow-y-auto px-1 pb-1">
            {showAutoDetect && (
              <button
                onClick={() => {
                  onChange(undefined);
                  setOpen(false);
                  setSearch("");
                }}
                className={`
                  w-full text-left px-3 py-2 rounded-xl text-sm transition-colors
                  ${value === undefined ? "text-accent-cyan bg-accent-cyan/10" : "text-slate-300 hover:bg-white/5 hover:text-white"}
                `}
              >
                Auto-detect
              </button>
            )}
            {filtered.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  onChange(lang.code);
                  setOpen(false);
                  setSearch("");
                }}
                className={`
                  w-full text-left px-3 py-2 rounded-xl text-sm transition-colors
                  ${value === lang.code ? (isCyan ? "text-accent-cyan bg-accent-cyan/10" : "text-accent-purple bg-accent-purple/10") : "text-slate-300 hover:bg-white/5 hover:text-white"}
                `}
              >
                {lang.name}
              </button>
            ))}
            {filtered.length === 0 && (
              <p className="px-3 py-2 text-sm text-slate-500">No results</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
