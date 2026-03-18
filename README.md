# Votee

Votee is a Korean-first avatar community service built with a React frontend and FastAPI backend.

## Structure

- `frontend`: Vite + React + TypeScript SPA.
- `backend`: FastAPI application, SQLAlchemy models, Alembic migrations, and pytest coverage.
- `docker-compose.yml`: local Docker stack for frontend, backend, Postgres, and Redis.
- `dockge.stack.yml`: Dockge stack that builds directly from the GitHub repository source.

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
5. Uploads are stored locally under `backend/uploads`.

## Dockge

Use [dockge.stack.yml](/C:/Users/dudtj/OneDrive/문서/Repo/votee/dockge.stack.yml) as the stack source in Dockge. It includes:

- `frontend`
- `backend`
- `db` (Postgres 16)
- `redis` (Redis 7 with AOF persistence)

For Dockge, you do not need a separate `.env` file. Enter the stack variables directly in Dockge's environment editor.

The Dockge stack does not require a separate server-side `git clone`. It uses Docker remote Git build contexts:

- `backend`: `https://github.com/ribeKim/votee.git#main:backend`
- `frontend`: `https://github.com/ribeKim/votee.git#main:frontend`

To switch the source branch or tag in Dockge, set these variables in the stack environment:

- `VOTEE_GIT_REPO`
- `VOTEE_GIT_REF`

The minimum backend variables to fill in Dockge are:

- `VOTEE_SESSION_SECRET`
- `VOTEE_FRONTEND_URL`
- `VOTEE_PUBLIC_APP_URL`
- `VOTEE_API_BASE_URL`
- `VOTEE_DISCORD_CLIENT_ID`
- `VOTEE_DISCORD_CLIENT_SECRET`
- `VOTEE_DISCORD_REDIRECT_URI`

When you want the latest code from GitHub, re-deploy the stack with build enabled so Docker rebuilds from the current Git ref.

## Deployment notes

- The repository is designed for a single VPS deployment using Docker Compose.
- The backend now expects `VOTEE_DATABASE_URL` and `VOTEE_REDIS_URL` to be reachable from the app container.
- File uploads are stored on the server volume mounted at `/app/uploads`.
