import { useState, useCallback } from "react";
import { TranslatePage } from "./components/TranslatePage";
import { LandingPage } from "./components/LandingPage";

type Page = "landing" | "app";

export default function App() {
  const [page, setPage] = useState<Page>("landing");
  const [visible, setVisible] = useState(true);

  const navigateTo = useCallback((target: Page) => {
    if (target === page) return;
    setVisible(false);
    setTimeout(() => {
      setPage(target);
      window.scrollTo({ top: 0 });
      // Double rAF ensures the DOM has painted the new page before fading in
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setVisible(true);
        });
      });
    }, 450);
  }, [page]);

  if (page === "landing") {
    return (
      <div
        className="page-transition"
        style={{
          opacity: visible ? 1 : 0,
          transform: visible
            ? "translateY(0) scale(1)"
            : "translateY(-8px) scale(0.99)",
        }}
      >
        <LandingPage onEnterApp={() => navigateTo("app")} />
      </div>
    );
  }

  return (
    <div
      className="page-transition"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible
          ? "translateY(0) scale(1)"
          : "translateY(8px) scale(0.99)",
      }}
    >
      <div className="min-h-screen flex flex-col">
        {/* Header */}
        <header
          data-testid="header"
          className="glass-strong sticky top-0 z-50 border-b border-glass-border"
        >
          <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
            <button
              onClick={() => navigateTo("landing")}
              className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
            >
              {/* Gradient logo */}
              <div
                data-testid="logo"
                className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center shadow-glow-cyan"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  strokeWidth="2"
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
              <h1 className="text-lg font-display font-semibold tracking-tight text-white">
                Fluently
              </h1>
            </button>

            {/* Dark mode toggle (decorative — always dark) */}
            <button className="w-9 h-9 rounded-full glass flex items-center justify-center text-slate-400 hover:text-white transition-colors">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1">
          <TranslatePage />
        </main>

        {/* Footer */}
        <footer className="py-6 text-center">
          <p className="text-xs text-slate-400/50 font-display font-medium tracking-wide">
            Encrypted &amp; locally stored.
          </p>
        </footer>
      </div>
    </div>
  );
}
