import { useState, useEffect, useRef } from "react";

interface LandingPageProps {
  onEnterApp: () => void;
}

// ── Data ─────────────────────────────────────────────────────

const TRANSLATIONS = [
  { code: "ES", lang: "Spanish", text: "Cada idioma abre una puerta a un mundo nuevo" },
  { code: "FR", lang: "French", text: "Chaque langue ouvre une porte vers un nouveau monde" },
  { code: "JA", lang: "Japanese", text: "すべての言語が新しい世界への扉を開く" },
  { code: "DE", lang: "German", text: "Jede Sprache öffnet eine Tür zu einer neuen Welt" },
  { code: "KO", lang: "Korean", text: "모든 언어는 새로운 세계로의 문을 엽니다" },
  { code: "AR", lang: "Arabic", text: "كل لغة تفتح باباً إلى عالم جديد" },
  { code: "ZH", lang: "Chinese", text: "每一种语言都打开了通往新世界的大门" },
  { code: "PT", lang: "Portuguese", text: "Cada idioma abre uma porta para um novo mundo" },
];

const HELLOS = [
  "Hello", "Hola", "Bonjour", "こんにちは", "Hallo", "Ciao",
  "안녕하세요", "Olá", "Привет", "مرحبا", "你好", "Hej",
  "Merhaba", "Γεια", "Sawubona", "नमस्ते", "สวัสดี", "Xin chào",
  "Habari", "Aloha", "Salut", "Hei", "Kamusta", "Salam",
];

const CAPABILITIES = [
  {
    title: "Text Translation",
    description:
      "Type or paste text and get instant translations. Auto-detects source language. No character limits, no throttling — translate as much as you want.",
    badge: "Live",
    badgeClass: "bg-accent-cyan/10 text-accent-cyan",
    icon: "text" as const,
    action: "Try text translation",
    stat: "Unlimited characters",
  },
  {
    title: "Image Translation",
    description:
      "Upload photos of signs, menus, or handwritten notes. Dual AI pipeline — OCR for printed text, vision model for handwriting. No competitor offers this locally.",
    badge: "Live",
    badgeClass: "bg-accent-purple/10 text-accent-purple",
    icon: "image" as const,
    action: "Try image translation",
    stat: "Handwriting recognition",
  },
  {
    title: "Document Translation",
    description:
      "Translate entire PDFs with layout-aware formatting. Export as Markdown, LaTeX, or plaintext with headings, tables, and structure preserved. Non-PDF formats supported too.",
    badge: "Live",
    badgeClass: "bg-landing-blue/10 text-landing-blue",
    icon: "document" as const,
    action: "Try document translation",
    stat: "Multi-format export",
  },
  {
    title: "PII Detection & Redaction",
    description:
      "Scan documents for personal data before translating. Regex catches emails, phones, and SSNs. AI detects names and addresses. Choose to mask, anonymize, or replace with synthetic data.",
    badge: "New",
    badgeClass: "bg-amber-500/10 text-amber-400",
    icon: "shield" as const,
    action: "Try PII redaction",
    stat: "Hybrid regex + AI",
  },
];

const COMPARISON_ROWS = [
  { feature: "Price", fluently: "Free forever", deepl: "From $8.99/mo", google: "Free w/ limits" },
  { feature: "Privacy", fluently: "100% on-device", deepl: "Cloud (texts may be stored)", google: "Cloud (used for training)" },
  { feature: "Offline", fluently: "Always works offline", deepl: "Requires internet", google: "Partial (language packs)" },
  { feature: "Image translation", fluently: "OCR + handwriting AI", deepl: "Not available", google: "Basic OCR only" },
  { feature: "Document translation", fluently: "Unlimited", deepl: "5–20 files/mo (paid)", google: "API only ($20/1M chars)" },
  { feature: "Format export", fluently: "Plain, Markdown, LaTeX", deepl: "Original format only", google: "Not available" },
  { feature: "PII redaction", fluently: "Built-in (regex + AI)", deepl: "Not available", google: "Separate DLP product" },
  { feature: "Character limits", fluently: "None", deepl: "1M/mo (Starter)", google: "5K per request (API)" },
  { feature: "Open source", fluently: "Yes, fully", deepl: "No", google: "No" },
  { feature: "Languages", fluently: "50+", deepl: "36", google: "249" },
];

const TRUST_ITEMS = [
  {
    value: "0 bytes",
    label: "sent to cloud",
    color: "#06b6d4",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
  },
  {
    value: "$0",
    label: "forever",
    color: "#8b5cf6",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="1" x2="12" y2="23" /><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    ),
  },
  {
    value: "50+",
    label: "languages",
    color: "#006DC7",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#006DC7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
    ),
  },
  {
    value: "100%",
    label: "open source",
    color: "#6366F1",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
      </svg>
    ),
  },
];

const STEPS = [
  {
    step: "01",
    title: "Input",
    description: "Type text, upload an image, or drop a document. Auto-language detection handles the rest. Optionally scan for PII first.",
    color: "#06b6d4",
  },
  {
    step: "02",
    title: "Translate",
    description: "On-device AI processes everything locally. PDFs get layout-aware extraction that preserves headings, tables, and structure.",
    color: "#006DC7",
  },
  {
    step: "03",
    title: "Export",
    description: "Copy, download as Markdown, LaTeX, or plaintext. No sign-up, no usage meters, no limits.",
    color: "#8b5cf6",
  },
];

// ── Components ───────────────────────────────────────────────

function ScrollReveal({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${className}`}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(32px)",
        transitionDelay: `${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

function CapabilityIcon({ type }: { type: "text" | "image" | "document" | "shield" }) {
  const props = {
    width: 22, height: 22, viewBox: "0 0 24 24", fill: "none",
    stroke: "#94A3B8", strokeWidth: 1.5,
    strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
  };
  if (type === "text")
    return (
      <svg {...props}>
        <path d="M5 8l6 6" /><path d="M4 14l6-6 2-3" /><path d="M2 5h12" /><path d="M7 2h1" />
        <path d="M22 22l-5-10-5 10" /><path d="M14 18h6" />
      </svg>
    );
  if (type === "image")
    return (
      <svg {...props}>
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
    );
  if (type === "shield")
    return (
      <svg {...props}>
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    );
  return (
    <svg {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function MinusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

/** Render a small icon for comparison cell values */
function ComparisonCell({ value, isFluently }: { value: string; isFluently: boolean }) {
  const isPositive =
    value.includes("100%") || value.includes("Free") || value.includes("Unlimited") ||
    value.includes("Always") || value.includes("None") || value.includes("Yes") ||
    value.includes("OCR + handwriting") || value.includes("Built-in") ||
    value.includes("Plain, Markdown");
  const isNegative =
    value.includes("Not available") || value.includes("No") || value.includes("Requires internet");

  return (
    <td className={`py-3 px-4 text-sm ${isFluently ? "text-white font-medium" : "text-slate-400"}`}>
      <span className="flex items-center gap-2">
        {isFluently && isPositive ? <CheckIcon /> : isNegative ? <XIcon /> : !isFluently ? <MinusIcon /> : null}
        {value}
      </span>
    </td>
  );
}

// ── Fluently Logo SVG ────────────────────────────────────────

function FluentlyLogo({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="white"
      strokeWidth={size < 14 ? 3 : 2.5} strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 8l6 6" /><path d="M4 14l6-6 2-3" /><path d="M2 5h12" /><path d="M7 2h1" />
      <path d="M22 22l-5-10-5 10" /><path d="M14 18h6" />
    </svg>
  );
}

// ── Main Component ───────────────────────────────────────────

export function LandingPage({ onEnterApp }: LandingPageProps) {
  const [currentTranslation, setCurrentTranslation] = useState(0);
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTranslation((prev) => (prev + 1) % TRANSLATIONS.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    const waitlist = JSON.parse(localStorage.getItem("fluently-waitlist") || "[]");
    waitlist.push({ email, timestamp: Date.now() });
    localStorage.setItem("fluently-waitlist", JSON.stringify(waitlist));
    setSubmitted(true);
    setEmail("");
    setTimeout(() => setSubmitted(false), 4000);
  };

  const trans = TRANSLATIONS[currentTranslation] ?? TRANSLATIONS[0]!;

  return (
    <div className="min-h-screen bg-landing-bg text-white overflow-hidden">
      {/* ── Ambient Background ─────────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute w-[700px] h-[700px] rounded-full opacity-[0.06] animate-float-slow"
          style={{ top: "-15%", left: "-10%", background: "radial-gradient(circle, #06b6d4, transparent 70%)" }} />
        <div className="absolute w-[550px] h-[550px] rounded-full opacity-[0.04] animate-float-slow-alt"
          style={{ top: "25%", right: "-12%", background: "radial-gradient(circle, #8b5cf6, transparent 70%)" }} />
        <div className="absolute w-[450px] h-[450px] rounded-full opacity-[0.03] animate-float-slow-drift"
          style={{ bottom: "-8%", left: "25%", background: "radial-gradient(circle, #006DC7, transparent 70%)" }} />
        <div className="absolute inset-0 dot-grid opacity-30" />
      </div>

      {/* ── Header ─────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-white/[0.06]"
        style={{ background: "rgba(6,11,20,0.85)", backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)" }}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <FluentlyLogo size={16} />
            </div>
            <span className="text-base font-display font-semibold tracking-tight">Fluently</span>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            {["Features", "Compare", "How It Works", "Open Source"].map((item) => (
              <a key={item} href={`#${item.toLowerCase().replace(/\s+/g, "-")}`}
                className="text-[13px] text-slate-400 hover:text-white transition-colors">{item}</a>
            ))}
          </nav>

          <button onClick={onEnterApp}
            className="px-4 py-2 text-sm font-display font-medium rounded-lg bg-white/[0.07] border border-white/[0.08] text-white hover:bg-white/[0.12] transition-all">
            Open App
          </button>
        </div>
      </header>

      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 pt-20 pb-12 md:pt-32 md:pb-20">
        <div className="flex flex-col items-center text-center gap-7">
          {/* Status badge */}
          <div className="landing-fade-in flex items-center gap-3 px-4 py-2 rounded-full border border-white/[0.08] bg-white/[0.03]"
            style={{ animationDelay: "0ms" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-medium text-slate-300 tracking-wide">
              On-Device AI&ensp;&middot;&ensp;No Cloud&ensp;&middot;&ensp;Free &amp; Open Source
            </span>
          </div>

          {/* Headline */}
          <h1 className="landing-fade-in text-[2.75rem] md:text-[4.5rem] font-serif font-600 leading-[1.08] tracking-[-0.02em]"
            style={{ animationDelay: "100ms" }}>
            The translator that
            <br />
            <span className="bg-gradient-to-r from-accent-cyan via-landing-blue to-accent-purple bg-clip-text text-transparent">
              never phones home.
            </span>
          </h1>

          {/* Subtext */}
          <p className="landing-fade-in max-w-2xl text-lg md:text-xl text-slate-400 leading-relaxed"
            style={{ animationDelay: "200ms" }}>
            DeepL charges $9/mo and sends your text to the cloud. Google trains on your data.
            Fluently runs <em>entirely</em> on your device — text, images, and documents with formatting preservation and PII redaction — for free, forever.
          </p>

          {/* CTAs */}
          <div className="landing-fade-in flex flex-col sm:flex-row items-center gap-3"
            style={{ animationDelay: "300ms" }}>
            <button onClick={onEnterApp}
              className="group relative px-8 py-4 rounded-2xl text-white font-display font-semibold transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              style={{ background: "linear-gradient(135deg, #06b6d4, #8b5cf6)" }}>
              <span className="relative z-10 flex items-center gap-2">
                Start Translating — It's Free
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                  strokeLinecap="round" strokeLinejoin="round" className="transition-transform group-hover:translate-x-1">
                  <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                </svg>
              </span>
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-40 transition-opacity blur-xl"
                style={{ background: "linear-gradient(135deg, #06b6d4, #8b5cf6)" }} />
            </button>

            <a href="#" className="flex items-center gap-2 px-6 py-4 rounded-2xl text-slate-400 hover:text-white border border-white/[0.07] hover:border-white/[0.15] transition-all text-sm font-medium">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              View on GitHub
            </a>
          </div>
        </div>

        {/* ── Animated Demo Card ────────────────────────────── */}
        <div className="landing-fade-in mt-16 md:mt-20 max-w-2xl mx-auto" style={{ animationDelay: "500ms" }}>
          <div className="relative rounded-3xl overflow-hidden"
            style={{ background: "rgba(15,23,42,0.6)", border: "1px solid rgba(255,255,255,0.07)" }}>
            {/* Gradient border glow */}
            <div className="absolute -inset-px rounded-3xl pointer-events-none border-shimmer"
              style={{ background: "linear-gradient(135deg, rgba(6,182,212,0.2), transparent 40%, transparent 60%, rgba(139,92,246,0.2))" }} />

            <div className="relative p-8 md:p-10">
              {/* Source */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-[11px] font-display font-semibold tracking-[0.15em] text-accent-cyan/80 uppercase">
                  EN &middot; English
                </span>
              </div>
              <p className="text-xl md:text-2xl text-white leading-relaxed mb-8 font-serif italic">
                Every language opens a door to a new world
              </p>

              {/* Divider */}
              <div className="relative h-px mb-8">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />
              </div>

              {/* Target — animated */}
              <div className="flex items-center gap-3 mb-4">
                <span key={`label-${currentTranslation}`}
                  className="text-[11px] font-display font-semibold tracking-[0.15em] text-accent-purple/70 uppercase animate-text-reveal">
                  {trans.code} &middot; {trans.lang}
                </span>
              </div>
              <div className="min-h-[36px] md:min-h-[40px]">
                <p key={currentTranslation}
                  className="text-xl md:text-2xl text-white leading-relaxed font-serif italic animate-text-reveal"
                  style={{ direction: trans.code === "AR" ? "rtl" : "ltr" }}>
                  {trans.text}
                </p>
              </div>

              {/* Language dots */}
              <div className="flex items-center justify-center gap-1.5 mt-8">
                {TRANSLATIONS.map((_, i) => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full transition-all duration-300"
                    style={{
                      background: i === currentTranslation ? "#8b5cf6" : "rgba(255,255,255,0.1)",
                      transform: i === currentTranslation ? "scale(1.4)" : "scale(1)",
                    }} />
                ))}
              </div>
            </div>
          </div>

          {/* Subtle label below demo */}
          <p className="text-center text-xs text-slate-600 mt-4 font-display">
            Running locally with translategemma &middot; No API calls &middot; No data transmitted
          </p>
        </div>
      </section>

      {/* ── Stats Strip ────────────────────────────────────── */}
      <div className="relative z-10 py-12 border-y border-white/[0.04]">
        <div className="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          {TRUST_ITEMS.map((item) => (
            <div key={item.label} className="text-center">
              <div className="w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center"
                style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
                {item.icon}
              </div>
              <div className="text-2xl font-serif font-bold mb-0.5" style={{ color: item.color }}>
                {item.value}
              </div>
              <p className="text-xs text-slate-500 font-display">{item.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Language Ticker ─────────────────────────────────── */}
      <div className="relative z-10 py-6 overflow-hidden">
        <div className="flex animate-ticker whitespace-nowrap">
          {[...HELLOS, ...HELLOS].map((hello, i) => (
            <span key={i} className="inline-flex items-center gap-5 px-5 text-sm text-slate-500/40 font-medium">
              {hello}
              <span className="w-1 h-1 rounded-full bg-slate-600/30" />
            </span>
          ))}
        </div>
      </div>

      {/* ── Capabilities ───────────────────────────────────── */}
      <section id="features" className="relative z-10 max-w-6xl mx-auto px-6 py-24 md:py-32">
        <ScrollReveal>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-[2.75rem] font-serif tracking-[-0.02em] mb-4">
              Translate anything, safely
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto leading-relaxed">
              Text, images, and documents — all handled on your device with no limits.
              Export in multiple formats. Redact personal data before translating. No cloud, no compromises.
            </p>
          </div>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5">
          {CAPABILITIES.map((cap, i) => (
            <ScrollReveal key={cap.title} delay={i * 100}>
              <button onClick={onEnterApp}
                className="group w-full text-left rounded-2xl p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                style={{ background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.06)" }}>
                <div className="flex items-center gap-2 mb-5">
                  <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold tracking-wider uppercase ${cap.badgeClass}`}>
                    {cap.badge}
                  </span>
                  <span className="px-2.5 py-1 rounded-md text-[10px] font-medium tracking-wide bg-white/[0.03] text-slate-500">
                    {cap.stat}
                  </span>
                </div>

                <div className="w-12 h-12 rounded-xl mb-5 flex items-center justify-center"
                  style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
                  <CapabilityIcon type={cap.icon} />
                </div>

                <h3 className="text-lg font-display font-semibold text-white mb-2">{cap.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-6">{cap.description}</p>

                <span className="inline-flex items-center gap-1.5 text-sm font-medium text-accent-cyan group-hover:gap-2.5 transition-all">
                  {cap.action}
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                    strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                  </svg>
                </span>
              </button>
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* ── Comparison Table ────────────────────────────────── */}
      <section id="compare" className="relative z-10 max-w-4xl mx-auto px-6 pb-24 md:pb-32">
        <ScrollReveal>
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-[2.75rem] font-serif tracking-[-0.02em] mb-4">
              The cloud tax on translation
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto leading-relaxed">
              Every major translator sends your text to remote servers.
              Fluently keeps everything on your machine — with no feature compromises.
            </p>
          </div>
        </ScrollReveal>

        <ScrollReveal delay={100}>
          <div className="rounded-2xl overflow-hidden" style={{ background: "rgba(15,23,42,0.5)", border: "1px solid rgba(255,255,255,0.06)" }}>
            {/* Mobile: scroll hint */}
            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px]">
                <thead>
                  <tr className="border-b border-white/[0.06]">
                    <th className="py-4 px-4 text-left text-xs font-display font-semibold text-slate-500 uppercase tracking-wider w-[160px]">
                      Feature
                    </th>
                    <th className="py-4 px-4 text-left text-xs font-display font-semibold uppercase tracking-wider w-[200px]">
                      <span className="flex items-center gap-2 text-accent-cyan">
                        <div className="w-5 h-5 rounded bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
                          <FluentlyLogo size={10} />
                        </div>
                        Fluently
                      </span>
                    </th>
                    <th className="py-4 px-4 text-left text-xs font-display font-medium text-slate-500 uppercase tracking-wider">
                      DeepL
                    </th>
                    <th className="py-4 px-4 text-left text-xs font-display font-medium text-slate-500 uppercase tracking-wider">
                      Google Translate
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARISON_ROWS.map((row, i) => (
                    <tr key={row.feature} className={i < COMPARISON_ROWS.length - 1 ? "border-b border-white/[0.03]" : ""}>
                      <td className="py-3 px-4 text-sm text-slate-300 font-medium">{row.feature}</td>
                      <ComparisonCell value={row.fluently} isFluently={true} />
                      <ComparisonCell value={row.deepl} isFluently={false} />
                      <ComparisonCell value={row.google} isFluently={false} />
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Table footer CTA */}
            <div className="border-t border-white/[0.06] px-6 py-4 flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Comparison data as of February 2026. Prices reflect published tiers.
              </p>
              <button onClick={onEnterApp}
                className="text-xs font-display font-medium text-accent-cyan hover:text-accent-cyan/80 transition-colors flex items-center gap-1">
                Try Fluently free
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                  strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ── Privacy Deep-Dive ──────────────────────────────── */}
      <section className="relative z-10 py-20 md:py-28 border-y border-white/[0.04]">
        <div className="max-w-4xl mx-auto px-6">
          <ScrollReveal>
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <span className="inline-block px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase bg-accent-cyan/10 text-accent-cyan mb-6">
                  Privacy-first
                </span>
                <h2 className="text-3xl md:text-4xl font-serif tracking-[-0.02em] mb-5 leading-tight">
                  Your words never leave your device.
                </h2>
                <p className="text-slate-400 leading-relaxed mb-6">
                  Google Translate's free tier can use your translations to improve their models.
                  DeepL's free tier stores your texts temporarily. Even their paid plans process everything on remote servers.
                </p>
                <p className="text-slate-400 leading-relaxed">
                  Fluently runs a local AI model on your hardware. There's no server, no API key, no account.
                  Your translations exist only in your browser's memory — and disappear when you close the tab.
                </p>
              </div>
              <div className="flex flex-col gap-4">
                {[
                  { label: "No account required", desc: "Open the app and start translating. That's it." },
                  { label: "No network requests", desc: "Translation works in airplane mode. Zero outbound connections." },
                  { label: "Built-in PII redaction", desc: "Detect and mask emails, phone numbers, names, and addresses before translating sensitive documents." },
                  { label: "Nothing stored", desc: "Translations live in browser memory only. Close tab = gone." },
                  { label: "Auditable code", desc: "Fully open source. Read every line. Verify every claim." },
                ].map((item) => (
                  <div key={item.label} className="flex items-start gap-3 p-4 rounded-xl"
                    style={{ background: "rgba(6,182,212,0.04)", border: "1px solid rgba(6,182,212,0.08)" }}>
                    <div className="mt-0.5 shrink-0">
                      <CheckIcon />
                    </div>
                    <div>
                      <p className="text-sm font-display font-semibold text-white mb-0.5">{item.label}</p>
                      <p className="text-xs text-slate-400">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* ── How It Works ───────────────────────────────────── */}
      <section id="how-it-works" className="relative z-10 max-w-4xl mx-auto px-6 py-24 md:py-32">
        <ScrollReveal>
          <h2 className="text-3xl md:text-[2.75rem] font-serif tracking-[-0.02em] text-center mb-16">
            How it works
          </h2>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          <div className="hidden md:block absolute top-10 left-[20%] right-[20%] h-px bg-gradient-to-r from-accent-cyan/20 via-landing-blue/20 to-accent-purple/20" />

          {STEPS.map((step, i) => (
            <ScrollReveal key={step.step} delay={i * 150}>
              <div className="text-center relative">
                <div className="w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center"
                  style={{ background: `${step.color}0A`, border: `1px solid ${step.color}18` }}>
                  <span className="text-2xl font-display font-bold" style={{ color: step.color }}>
                    {step.step}
                  </span>
                </div>
                <h3 className="text-lg font-display font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{step.description}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </section>

      {/* ── Coming Soon ────────────────────────────────────── */}
      <section id="open-source" className="relative z-10 max-w-4xl mx-auto px-6 pb-24 md:pb-32">
        <ScrollReveal>
          <h2 className="text-3xl md:text-[2.75rem] font-serif tracking-[-0.02em] text-center mb-4">
            On the horizon
          </h2>
          <p className="text-slate-400 text-center mb-12 max-w-lg mx-auto leading-relaxed">
            We're building more ways to break language barriers — all open source.
          </p>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { title: "Website Translation", description: "Translate entire websites by URL. Coming with a browser extension." },
            { title: "API Access", description: "Integrate Fluently's translation engine into your own applications." },
            { title: "Mobile App", description: "Native iOS and Android apps with the same local-first architecture." },
          ].map((item, i) => (
            <ScrollReveal key={item.title} delay={i * 100}>
              <div className="rounded-2xl p-6"
                style={{ background: "rgba(15,23,42,0.3)", border: "1px solid rgba(255,255,255,0.04)" }}>
                <span className="inline-block px-2.5 py-1 rounded-md text-[10px] font-bold tracking-wider uppercase bg-white/[0.04] text-slate-500 mb-4">
                  Coming Soon
                </span>
                <h3 className="text-base font-display font-semibold text-white/80 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{item.description}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>

        {/* Email signup */}
        <ScrollReveal delay={200}>
          <div className="mt-8 max-w-md mx-auto">
            <div className="rounded-2xl p-5"
              style={{ background: "rgba(15,23,42,0.4)", border: "1px solid rgba(255,255,255,0.06)" }}>
              <p className="text-sm text-slate-300 text-center mb-4">Get notified when new features launch</p>
              <form onSubmit={handleEmailSubmit} className="flex gap-2">
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@email.com" required
                  className="flex-1 px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-white placeholder:text-slate-600 text-sm focus:outline-none focus:border-accent-cyan/30 transition-colors" />
                <button type="submit"
                  className="px-5 py-2.5 rounded-xl bg-white/[0.07] border border-white/[0.08] text-white text-sm font-medium hover:bg-white/[0.12] transition-all whitespace-nowrap">
                  Notify me
                </button>
              </form>
              {submitted && (
                <p className="mt-3 text-xs text-emerald-400 text-center animate-pulse">You're on the list!</p>
              )}
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ── Final CTA ──────────────────────────────────────── */}
      <section className="relative z-10 max-w-4xl mx-auto px-6 pb-24 md:pb-32">
        <ScrollReveal>
          <div className="relative rounded-3xl overflow-hidden p-10 md:p-16 text-center"
            style={{ background: "linear-gradient(135deg, rgba(6,182,212,0.07), rgba(139,92,246,0.07))", border: "1px solid rgba(255,255,255,0.06)" }}>
            <div className="absolute inset-0 pointer-events-none"
              style={{ background: "radial-gradient(circle at 50% 0%, rgba(6,182,212,0.08), transparent 60%)" }} />

            <h2 className="relative text-3xl md:text-[2.75rem] font-serif tracking-[-0.02em] mb-4">
              Ready to translate?
            </h2>
            <p className="relative text-slate-400 mb-8 max-w-md mx-auto leading-relaxed">
              No sign-up. No payment. No data leaves your device. Just open and start translating.
            </p>
            <div className="relative flex flex-col sm:flex-row items-center justify-center gap-3">
              <button onClick={onEnterApp}
                className="group px-8 py-4 rounded-2xl text-white font-display font-semibold transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                style={{ background: "linear-gradient(135deg, #06b6d4, #8b5cf6)" }}>
                <span className="flex items-center gap-2">
                  Open Fluently
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                    strokeLinecap="round" strokeLinejoin="round" className="transition-transform group-hover:translate-x-1">
                    <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                  </svg>
                </span>
              </button>
              <span className="text-xs text-slate-500">No account required</span>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-white/[0.04] py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <FluentlyLogo size={11} />
            </div>
            <span className="text-sm font-display font-medium text-slate-500">Fluently</span>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-600">
            <a href="#" className="hover:text-slate-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-slate-400 transition-colors">GitHub</a>
            <a href="#" className="hover:text-slate-400 transition-colors">License</a>
            <span>&copy; 2025 Fluently. Open source under MIT.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
