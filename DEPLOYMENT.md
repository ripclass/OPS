# OPS Deployment Guide

This repo is ready for a split deployment:

- `frontend/` -> Vercel
- `backend/` -> Render
- Supabase -> OPS temporal memory
- Zep -> graph and report tooling

Docker is optional for local development only. It is not required for the hosted deployment.

## Architecture

- Frontend: Vue 3 + Vite static app
- Backend: Flask API with long-running simulation/report jobs
- Persistent storage: Render disk mounted to `backend/uploads`
- Temporal continuity: Supabase
- Graph/report runtime: Zep + configured LLM backend

## 1. Backend on Render

### Create the service

- Service type: `Web Service`
- Runtime: `Python`
- Root directory: `backend`
- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --threads 8
```

- Health check path:

```text
/health
```

### Persistent disk

Attach a persistent disk:

- Name: `ops-uploads`
- Mount path:

```text
/opt/render/project/src/backend/uploads
```

- Suggested size: `10 GB` to start

This is required because the current backend persists:

- uploaded files
- extracted text
- simulation artifacts
- reports
- OPS profile snapshots

Set this backend env alongside the disk:

```text
UPLOAD_FOLDER=/opt/render/project/src/backend/uploads
```

### Backend environment variables

Set these in Render:

```text
SECRET_KEY=<strong random value>
FLASK_DEBUG=False
FRONTEND_ORIGIN=https://<your-vercel-domain>
UPLOAD_FOLDER=/opt/render/project/src/backend/uploads
LLM_API_KEY=<value>
LLM_BASE_URL=<value>
LLM_MODEL_NAME=<value>
ZEP_API_KEY=<value>
SUPABASE_URL=<value>
SUPABASE_SERVICE_ROLE_KEY=<value>
```

Optional:

```text
FRONTEND_ORIGINS=https://<your-vercel-domain>,https://<custom-domain>
OASIS_SIMULATION_DATA_DIR=/opt/render/project/src/backend/uploads/simulations
```

### Render blueprint

You can also deploy from the included:

- [render.yaml](/J:/OPS/OPS/render.yaml)

## 2. Frontend on Vercel

### Create the project

- Root directory: `frontend`
- Framework preset: `Vite`
- Build command:

```bash
npm run build
```

- Output directory:

```text
dist
```

### Frontend environment variables

Set these in Vercel:

```text
VITE_API_BASE_URL=https://<your-render-domain>
VITE_DEMO_MODE=false
VITE_STRIPE_CHECKOUT_URL=<optional>
VITE_CALENDLY_URL=<optional>
```

The SPA rewrite is already included in:

- [frontend/vercel.json](/J:/OPS/OPS/frontend/vercel.json)

This is required because the app uses history-mode Vue Router.

## 3. Supabase

Temporal continuity depends on Supabase.

Required backend envs:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

If you have not created the memory table yet, use:

```sql
CREATE TABLE ops_agent_states (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_user_id integer NOT NULL,
    project_id text NOT NULL,
    agent_name text,
    simulation_history jsonb DEFAULT '[]',
    baseline_anxiety float DEFAULT 5.0,
    current_trust_government integer,
    current_shame_sensitivity integer,
    cumulative_stress float DEFAULT 0.0,
    last_simulation_date text,
    updated_at timestamp DEFAULT now(),
    UNIQUE(agent_user_id, project_id)
);
```

## 4. Zep

The current OPS graph/report path still depends on Zep.

Required backend env:

```text
ZEP_API_KEY
```

If `ZEP_API_KEY` is missing, the backend starts, but graph-backed functions are limited.

## 5. LLM provider

This backend expects an OpenAI-compatible API.

Required backend envs:

```text
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL_NAME
```

Example patterns:

- OpenAI-compatible hosted gateway
- Ollama with OpenAI compatibility
- other proxy providers exposing `/v1`

## 6. Launch checklist

Before exposing the app beyond private staging:

1. Deploy backend to Render.
2. Attach the persistent disk.
3. Set all backend env vars.
4. Deploy frontend to Vercel.
5. Set frontend env vars.
6. Confirm Vercel can reach Render.
7. Confirm `/health` returns OK.
8. Confirm direct refresh works on:
   - `/`
   - `/process/:projectId`
   - `/simulation/:simulationId`
   - `/simulation/:simulationId/start`
   - `/report/:reportId`
   - `/interaction/:reportId`

## 7. Private staging smoke test

Run these before public release:

### A. Source ingestion

- upload a PDF
- submit one public news URL
- submit mixed file + URL

### B. OPS flow

Run at least:

- Bangladesh
- India
- Pakistan
- Nepal
- Sri Lanka

For each run, verify:

- Step 2 population config persists
- Step 3 simulation completes
- Step 4 report completes
- Step 5 chat opens
- live batch interview works

### C. Temporal continuity

- run the same project twice
- confirm agent memory persists in Supabase

### D. Artifact persistence

- redeploy backend
- confirm old reports and simulation artifacts still exist

## 8. Known notes

- The frontend build must be run from the canonical repo path, not through the Windows junction path, or Vite may fail with an emitted-path error.
- The app is stable enough for private ship-testing, but report richness can still be improved over time.
- Current hosted deployment does not require Docker.
