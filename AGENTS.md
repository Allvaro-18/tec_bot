# AGENTS.md

## Layout
- `backend/` — FastAPI; entrada en `app/main.py`, rutas en `app/api/routes.py`, tests en `tests/`.
- `frontend/` — React + Vite + TypeScript; entrada en `src/main.tsx`.
- En desarrollo Vite hace proxy de `/api` a `http://localhost:8000`; no hace falta CORS.

## Commands
Backend (desde `backend/`):
- `pip install -r requirements-dev.txt`
- `uvicorn app.main:app --reload --port 8000`
- `pytest` — un test: `pytest tests/test_api.py::test_chat`

Frontend (desde `frontend/`):
- `npm install`
- `npm run dev`
- `npm run build` — typecheck + build

## Notes
- La API vive bajo `/api`; en el frontend usa rutas relativas en desarrollo.
- Config del backend: prefijo `TECBOT_` y archivo `backend/.env`.
- No hay runner de tests en el frontend todavía.
