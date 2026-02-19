import { TranslatePage } from "./components/TranslatePage";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-fluently-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">F</span>
            </div>
            <h1 className="text-xl font-semibold tracking-tight">Fluently</h1>
          </div>
          <p className="text-sm text-gray-400 hidden sm:block">
            Translate everything.
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <TranslatePage />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-5xl mx-auto px-4 py-4 text-center text-xs text-gray-400">
          Fluently — Fast, private translation powered by AI.
          <span className="mx-2">·</span>
          176 languages supported
        </div>
      </footer>
    </div>
  );
}
