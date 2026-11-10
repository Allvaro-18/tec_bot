from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.services.bot import generate_reply

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(reply=generate_reply(payload.message))
