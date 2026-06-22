# FleetCare AI — Predictive Fleet Maintenance Platform

A multi-tenant SaaS platform that uses machine learning to predict tyre wear and maintenance needs across commercial vehicle fleets.

**Stack:** Django 5 · DRF · PostgreSQL · React 18 · Recharts · scikit-learn · gunicorn · WhiteNoise

---

## Table of Contents

1. [Local Setup](#local-setup)
2. [Environment Variables](#environment-variables)
3. [Backend Deployment — Render](#backend-deployment--render)
4. [Frontend Deployment — Vercel](#frontend-deployment--vercel)
5. [Database Setup](#database-setup)
6. [Running the Simulator](#running-the-simulator)
7. [Troubleshooting](#troubleshooting)

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
cd backend

# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, DJANGO_DEBUG=True

# 4. Run migrations
python manage.py migrate

# 5. Create a superuser (optional)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Backend runs at: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at: http://localhost:3000

> The frontend proxies `/api/*` requests to `localhost:8000` via the `proxy` field in `package.json`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Django cryptographic signing key |
| `DJANGO_DEBUG` | No | `False` | Set `True` for local development only |
| `ALLOWED_HOSTS` | Yes | `localhost,127.0.0.1` | Comma-separated allowed hostnames |
| `DATABASE_URL` | No | SQLite fallback | PostgreSQL connection string |
| `CORS_ALLOWED_ORIGINS` | Production | — | Comma-separated frontend origins |
| `JWT_ACCESS_MINUTES` | No | `1440` | Access token lifetime (minutes) |
| `JWT_REFRESH_DAYS` | No | `7` | Refresh token lifetime (days) |

**Generate a SECRET_KEY:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Backend Deployment — Render

### Option A: Blueprint (render.yaml) — Recommended

1. Push code to GitHub
2. In Render dashboard: **New** > **Blueprint** > Connect repository
3. Render reads `render.yaml` and provisions the web service + PostgreSQL database automatically
4. After deploy, update these env vars in the Render dashboard:
   - `ALLOWED_HOSTS` — add your `.onrender.com` hostname
   - `CORS_ALLOWED_ORIGINS` — add your Vercel frontend URL

### Option B: Manual Web Service

| Field | Value |
|---|---|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate --no-input` |
| **Start Command** | `gunicorn backend.wsgi:application --workers 2 --timeout 120` |
| **Python Version** | `3.11` |

Add all environment variables from the table above in the Render dashboard.

### Post-Deploy Steps

```bash
# Create admin user via Render shell tab
python manage.py createsuperuser

# Register your company at:
# https://your-backend.onrender.com/api/auth/register
```

---

## Frontend Deployment — Vercel

1. Push code to GitHub
2. Vercel dashboard: **New Project** > Import repository
3. Set **Root Directory** to `frontend`
4. Add environment variable: `REACT_APP_API_URL` = `https://your-backend.onrender.com/api`
5. Update `frontend/src/services/api.js` line 1:

```js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

6. Vercel runs `npm run build` automatically on deploy

> After getting your Vercel URL, add it to `CORS_ALLOWED_ORIGINS` in Render env vars.

---

## Database Setup

### Local — SQLite (automatic)

No configuration needed. `db.sqlite3` is created automatically on first `migrate`.

### Production — PostgreSQL on Render

Render injects `DATABASE_URL` automatically when using `render.yaml`. Migrations run during the build command. No manual steps needed.

---

## Running the Simulator

The telemetry simulator generates realistic fleet data per registered company.

**Via API:**

```bash
curl -X POST https://your-backend.onrender.com/api/simulator/start \
  -H "Authorization: Bearer <your_access_token>"
```

**Via Dashboard UI:** Use the "Start Simulator" button in the top navbar.

The simulator is idempotent — starting it multiple times will not create duplicate vehicles or fleets.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ImproperlyConfigured: SECRET_KEY not set` | Production mode requires explicit key | Add `SECRET_KEY` to env vars |
| `DisallowedHost` | Hostname not in `ALLOWED_HOSTS` | Add hostname to `ALLOWED_HOSTS` env var |
| CORS blocked in browser | Frontend origin missing | Add Vercel URL to `CORS_ALLOWED_ORIGINS` |
| `net::ERR_CONNECTION_REFUSED` | Backend not running | Start with `python manage.py runserver` |
| `collectstatic` fails | WhiteNoise misconfigured | Verify WhiteNoise is in `MIDDLEWARE` |
| PostgreSQL connection refused | Wrong `DATABASE_URL` | Format: `postgres://USER:PASS@HOST:PORT/DB` |
