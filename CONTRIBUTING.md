# Contributing to Fluently

## Repo Layout

```
fluently/
├── backend/     ← Python (FastAPI)   — Friend owns core API
├── frontend/    ← TypeScript (React) — Myko owns UI
├── docs/        ← Shared
└── ...
```

## Branch Strategy

```
main                    ← always deployable, protected
├── dev                 ← integration branch, PR target
├── feat/text-input     ← feature branches off dev
├── feat/pdf-pipeline
├── fix/detection-bug
└── ...
```

**Rules:**
- Never push directly to `main` or `dev`.
- All work goes through feature branches → PR to `dev`.
- `dev` → `main` merges happen when a milestone is stable.
- Branch naming: `feat/`, `fix/`, `chore/`, `docs/` prefixes.

## Development Workflow

### 1. Setup

```bash
git clone https://github.com/<org>/fluently.git
cd fluently
cp .env.example .env

# Backend
cd backend && uv sync && cd ..

# Frontend
cd frontend && npm install && cd ..

# Or just:
make setup
```

### 2. Running locally

```bash
# Everything at once:
make dev

# Or individually:
make backend    # FastAPI on :8000
make frontend   # Vite on :5173
make ollama     # Ollama serve (if not already running)
```

### 3. Before committing

```bash
make lint       # Run all linters
make test       # Run all tests
make check      # lint + test
```

### 4. Pull Requests

- Write a clear description of **what** and **why**.
- Link to a roadmap item or issue if applicable.
- CI must pass (lint + test + type-check).
- At least one review from the other person.
- Squash merge to keep history clean.

## Code Standards

### Backend (Python)

- **Formatter**: `black` (line length 88)
- **Import sorting**: `isort` (black profile)
- **Type checking**: `pyright` strict mode
- **Testing**: `pytest` + `pytest-asyncio`
- **Style**: Type hints on all function signatures. Docstrings on public functions.

### Frontend (TypeScript)

- **Formatter**: Prettier (defaults)
- **Linter**: ESLint (strict TypeScript rules)
- **Style**: Functional components, hooks, no class components. Named exports.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(frontend): add language selector component
fix(backend): handle empty text array in translation
docs: update architecture diagram
chore: add docker compose for dev
```

## Communication

- **API contract changes**: Always discuss before changing request/response shapes. Update the OpenAPI schema and notify the other person.
- **Shared code**: `docs/` is shared territory. Both people maintain their section.
- **Breaking changes**: Never merge a breaking backend change without a matching frontend update (or vice versa).
