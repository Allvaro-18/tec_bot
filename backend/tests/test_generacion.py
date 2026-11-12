"""Pruebas de la generación con Ollama usando un cliente simulado."""

import sys
import types

import pytest

from app.config import settings
from app.services import rag

FRAGMENTOS = [rag.Fragmento(documento="servicio-social.md", texto="Requisitos: 60% de créditos.")]


def _ollama_falso(respuesta: str | None = None, error: Exception | None = None):
    llamadas: list[dict] = []

    class Cliente:
        def __init__(self, host: str, timeout: float) -> None:
            pass

        def chat(self, **kwargs):
            llamadas.append(kwargs)
            if error:
                raise error
            return {"message": {"content": respuesta}}

    modulo = types.ModuleType("ollama")
    modulo.Client = Cliente
    return modulo, llamadas


@pytest.fixture
def con_ollama():
    settings.usar_ollama = True
    yield


def test_usa_respuesta_de_ollama(con_ollama, monkeypatch) -> None:
    modulo, llamadas = _ollama_falso("Necesitas el 60% de créditos [servicio-social.md].")
    monkeypatch.setitem(sys.modules, "ollama", modulo)

    texto = rag._generar_con_ollama("¿Qué necesito?", FRAGMENTOS)

    assert texto == "Necesitas el 60% de créditos [servicio-social.md]."
    prompt = llamadas[0]["messages"][0]["content"]
    assert "[servicio-social.md]" in prompt and "¿Qué necesito?" in prompt
    assert llamadas[0]["model"] == settings.ollama_model


def test_si_ollama_falla_devuelve_none(con_ollama, monkeypatch) -> None:
    modulo, _ = _ollama_falso(error=ConnectionError("Ollama apagado"))
    monkeypatch.setitem(sys.modules, "ollama", modulo)

    assert rag._generar_con_ollama("¿Qué necesito?", FRAGMENTOS) is None


def test_desactivado_no_llama_a_ollama(monkeypatch) -> None:
    modulo, llamadas = _ollama_falso("no debería usarse")
    monkeypatch.setitem(sys.modules, "ollama", modulo)

    assert rag._generar_con_ollama("¿Qué necesito?", FRAGMENTOS) is None
    assert llamadas == []
