# TEC Bot

FastAPI + React (Vite + TypeScript).

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

Tests:

```powershell
cd backend
pytest
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

http://localhost:5173 — Vite reenvía `/api` al backend en el puerto 8000.
