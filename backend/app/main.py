from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routes import router
from app.config import settings

PAGINA_CHAT = Path(__file__).resolve().parent / "chat.html"

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def pagina_chat() -> HTMLResponse:
    """Interfaz web sencilla (sin npm) servida por la misma API."""
    return HTMLResponse(PAGINA_CHAT.read_text(encoding="utf-8"))
