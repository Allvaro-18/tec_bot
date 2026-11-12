"""Configuración común de pytest.

Las pruebas no llaman al modelo real de Ollama: serían lentas y sus respuestas
cambian en cada ejecución. La generación se prueba con un Ollama simulado en
tests/test_generacion.py.
"""

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def sin_ollama_real():
    original = settings.usar_ollama
    settings.usar_ollama = False
    yield
    settings.usar_ollama = original
