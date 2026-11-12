from fastapi import APIRouter

from app.config import settings
from app.schemas import ConsultaRequest, ConsultaResponse, SaludResponse
from app.services.rag import consultar

router = APIRouter()


@router.get("/salud", response_model=SaludResponse)
@router.get("/health", response_model=SaludResponse, include_in_schema=False)
def salud() -> SaludResponse:
    return SaludResponse(estado="ok")


@router.post("/consultas", response_model=ConsultaResponse)
def consultas(payload: ConsultaRequest) -> ConsultaResponse:
    # Valida (Pydantic) -> recupera (ChromaDB) -> devuelve el contrato acordado.
    resultado = consultar(payload.pregunta, settings.corpus_path)
    return ConsultaResponse(**resultado)
