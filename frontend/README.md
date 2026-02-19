# Fluently Frontend

React + Vite + TypeScript + TailwindCSS.

## Setup

```bash
npm install
npm run dev
```

Runs at `http://localhost:5173`. API requests are proxied to `http://localhost:8000` via Vite's dev server.

## Structure

```
frontend/
├── src/
│   ├── main.tsx              # React entry point
│   ├── App.tsx               # Root component (header, layout, footer)
│   ├── components/
│   │   ├── TranslatePage.tsx  # Main translation UI
│   │   └── LanguageSelector.tsx
│   ├── hooks/
│   │   └── useTranslation.ts # Debounced API call hook
│   ├── services/
│   │   └── api.ts            # Typed API client
│   └── types/
│       └── index.ts          # Shared types + language list
├── public/
├── index.html
├── vite.config.ts            # Dev server + API proxy config
├── tailwind.config.js
└── package.json
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` (proxied) | Backend API base URL |

## Build

```bash
npm run build     # outputs to dist/
npm run preview   # preview production build locally
```
