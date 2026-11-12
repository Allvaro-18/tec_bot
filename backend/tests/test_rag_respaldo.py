"""Pruebas de la búsqueda de respaldo por palabras clave (sin ChromaDB)."""

from app.config import settings
from app.services.rag import buscar_fragmentos


def test_respaldo_encuentra_servicio_social() -> None:
    hallazgos = buscar_fragmentos("¿Qué necesito para el servicio social?", settings.corpus_path)
    assert hallazgos and hallazgos[0].documento == "servicio-social.md"


def test_respaldo_sin_evidencia_cafeteria() -> None:
    # "horario" aparece en servicio-social.md, pero una sola palabra suelta no es evidencia.
    assert buscar_fragmentos("¿Cuál es el horario de la cafetería?", settings.corpus_path) == []
