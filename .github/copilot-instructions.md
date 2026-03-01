# Copilot Instructions for ATS Platform

## Big picture (what’s actually wired)
- Two backend implementations exist: **FastAPI (Python)** under backend/app and an **Express (TypeScript)** scaffold under backend/src. Docker Compose uses the **FastAPI** backend (port 8000) and Celery worker.
- The frontend is a **Vite React app** under frontend/src (port 5173 by default). A Next.js-style app directory exists under frontend/app, but package.json does not include Next.js dependencies—treat it as a future/unused scaffold unless you add Next.js.
- Data layer is PostgreSQL + pgvector. Models live in backend/app/models and use SQLAlchemy 2.0 async + pgvector (e.g., Candidate/Job/Application models).

## Key flows and boundaries
- FastAPI lifecycle: startup initializes DB in backend/app/main.py via init_db() from backend/app/database.py.
- Services for AI and parsing are in backend/app/services (ai_service.py, parser_service.py). AI uses OpenAI client; parsing handles PDF/DOCX/TXT.
- Frontend API client is in frontend/lib/api.ts and targets /api/v1 endpoints on NEXT_PUBLIC_API_URL (defaults to http://localhost:8000).

## Critical workflows (verify before coding)
- Docker-first stack: docker-compose.yml starts Postgres, Redis, FastAPI, Celery worker, and frontend. FastAPI is bound to 8000.
- Local FastAPI dev: uvicorn app.main:app --reload (backend/). Alembic migrations are configured under backend/alembic.
- Local Vite dev: npm run dev (frontend/). Expect Vite on 5173 unless you change the port.
- Express backend dev: npm run dev (backend/) uses nodemon on backend/src/index.ts and binds to PORT (default 3000). This is **not** used by docker-compose.

## Project-specific conventions and gotchas
- Choose which backend you’re extending (FastAPI vs Express) and keep ports aligned with the frontend health check. frontend/src/App.tsx currently calls http://localhost:3000/health (Express), while docker-compose expects FastAPI at 8000.
- Async SQLAlchemy session is provided via get_db() in backend/app/database.py; models inherit from Base and TimeStampMixin.
- CORS origins are configured from Settings.allowed_origins in backend/app/config.py (comma-separated string).

## Examples to anchor work
- FastAPI entry point: backend/app/main.py
- SQLAlchemy models with pgvector: backend/app/models/candidate.py, backend/app/models/job.py
- API client and auth token handling: frontend/lib/api.ts

Keep instructions consistent with the chosen stack, and update mismatched ports or env vars when implementing features.