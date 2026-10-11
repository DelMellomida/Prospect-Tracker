# Prospect Tracker — Compact Overview

## Stack
- **Backend**: Django (Python 3.13), DRF, `tracker` app, `docker-compose.yml`
- **Frontend**: Next.js + TypeScript + Tailwind (`frontend/app/`)
- **Env**: `.env` / `.env.example` (Django + Next.js vars)

## Key Paths
- Backend config: `backend/config/`
- App logic: `backend/tracker/` (models, serializers, views, filters, pagination, services)
- Tests: `backend/tracker/tests/`
- Frontend entry: `frontend/app/page.tsx`, `layout.tsx`
- Design docs: `docs/` (PDF + DOCX + flow diagrams)

## Commands
- `docker-compose up` — full stack
- `cd backend && python -m pytest` (uses `.venv`, `test_settings`)
- `cd frontend && npm run dev`

## Notes
- Ruff configured (`line-length = 100`, `quote-style = 'single'`)
- Migrations excluded from lint
- `.env` should not be committed (`.gitignore` present)
