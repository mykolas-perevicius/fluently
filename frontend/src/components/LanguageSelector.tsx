import { COMMON_LANGUAGES } from "../types";

interface LanguageSelectorProps {
  value: string | undefined;
  onChange: (code: string | undefined) => void;
  showAutoDetect?: boolean;
  label: string;
}

export function LanguageSelector({
  value,
  onChange,
  showAutoDetect = false,
  label,
}: LanguageSelectorProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
        {label}
      </label>
      <select
        value={value ?? "__auto__"}
        onChange={(e) => {
          const v = e.target.value;
          onChange(v === "__auto__" ? undefined : v);
        }}
        className="
          px-3 py-2 rounded-lg
          bg-white dark:bg-gray-800
          border border-gray-200 dark:border-gray-700
          text-sm font-medium
          focus:outline-none focus:ring-2 focus:ring-fluently-500 focus:border-transparent
          cursor-pointer
        "
      >
        {showAutoDetect && (
          <option value="__auto__">Auto-detect</option>
        )}
        {COMMON_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}
