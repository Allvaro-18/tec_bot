"""Pruebas de la búsqueda semántica con ChromaDB (Día 3).

Se omiten automáticamente si chromadb no está instalado. La primera ejecución
descarga el modelo de embeddings, por lo que necesita internet una vez.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("chromadb")

from app.config import settings  # noqa: E402
from app.services import rag  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))

import indexar  # noqa: E402


@pytest.fixture(scope="module")
def indice_temporal(tmp_path_factory: pytest.TempPathFactory):
    """Construye un índice aislado para no depender del chroma_db/ local."""
    ruta = tmp_path_factory.mktemp("chroma_db")
    indexar.indexar(documentos_dir=RAIZ / "documentos-demo", chroma_path=ruta)

    original = settings.chroma_dir
    settings.chroma_dir = str(ruta)
    rag._obtener_coleccion.cache_clear()
    yield ruta
    settings.chroma_dir = original
    rag._obtener_coleccion.cache_clear()


def test_dividir_texto_respeta_tamano() -> None:
    texto = "\n\n".join(f"Párrafo {i} " + "x" * 300 for i in range(10))
    fragmentos = indexar.dividir_texto(texto, tamano=800, solapamiento=120)
    assert len(fragmentos) > 1
    # Cada fragmento cabe en el tamaño + solapamiento.
    assert all(len(f) <= 800 + 120 + 2 for f in fragmentos)


def test_indexa_los_cuatro_documentos(indice_temporal: Path) -> None:
    import chromadb

    coleccion = chromadb.PersistentClient(path=str(indice_temporal)).get_collection(
        settings.coleccion
    )
    metadatos = coleccion.get(include=["metadatas"])["metadatas"]
    documentos = {m["documento"] for m in metadatos}
    assert documentos == {
        "servicio-social.md",
        "residencias-profesionales.md",
        "titulacion.md",
        "acreditacion-academica.md",
    }


def test_recuperar_servicio_social_en_top3(indice_temporal: Path) -> None:
    resultados = rag.recuperar("¿Qué necesito para iniciar el servicio social?")
    top3 = [r["documento"] for r in resultados[:3]]
    assert "servicio-social.md" in top3
    assert all(0.0 <= r["distancia"] <= 2.0 for r in resultados)


def test_consulta_servicio_social_cita_su_documento(indice_temporal: Path) -> None:
    # Aquí se prueba que la fuente citada sea la correcta, sin depender del umbral.
    # El umbral real se prueba en test_api.py (casos con y sin evidencia).
    original = settings.umbral_distancia
    settings.umbral_distancia = 2.0
    try:
        resultado = rag.consultar("¿Qué necesito para el servicio social?")
    finally:
        settings.umbral_distancia = original
    assert resultado["fuentes"][0]["documento"] == "servicio-social.md"
