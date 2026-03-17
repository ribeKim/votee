# Votee

Votee is a Korean-first avatar community service built with a React frontend and FastAPI backend.

## Structure

- `frontend`: Vite + React + TypeScript SPA.
- `backend`: FastAPI application, SQLAlchemy models, Alembic migrations, and pytest coverage.
- `docker-compose.yml`: local Docker stack for frontend, backend, Postgres, and Redis.
- `dockge.stack.yml`: Dockge-friendly stack file using the same services and volumes.

## Environment

Copy `.env.example` to `.env` and fill in the Discord OAuth2 credentials before using the real login flow.

The default environment is now aligned to local Docker services:

- Postgres: `db:5432`
- Redis: `redis:6379`
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:4173`

## Local development

1. Copy `.env.example` to `.env`.
2. Start the full stack with `docker compose up --build`.
3. Open the frontend at `http://localhost:4173`.
4. Check backend dependency status at `http://localhost:8000/api/health`.
5. Uploads are stored locally under `backend/uploads` unless you later switch to Supabase storage.

## Dockge

Use [dockge.stack.yml](/C:/Users/dudtj/OneDrive/문서/Repo/votee/dockge.stack.yml) as the stack source in Dockge. It includes:

- `frontend`
- `backend`
- `db` (Postgres 16)
- `redis` (Redis 7 with AOF persistence)

## Deployment notes

- The repository is designed for a single VPS deployment using Docker Compose.
- The backend now expects `VOTEE_DATABASE_URL` and `VOTEE_REDIS_URL` to be reachable from the app container.
- Production file uploads can continue using local storage or switch `VOTEE_STORAGE_DRIVER` to `supabase`.
