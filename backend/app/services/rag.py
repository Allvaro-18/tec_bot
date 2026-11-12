"""Recuperación documental de TecBot Académico.

Motor principal: ChromaDB (búsqueda semántica, Día 3).
Respaldo: búsqueda por palabras clave sobre documentos-demo/, que se usa solo si
ChromaDB no está instalado o el índice todavía no se ha generado.
Generación (opcional): Ollama redacta la respuesta a partir de los fragmentos
recuperados. Si Ollama no está disponible, se devuelve un resumen del fragmento.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

ADVERTENCIA = (
    "La información proviene de documentos de demostración y no constituye normativa oficial."
)
RESPUESTA_SIN_EVIDENCIA = (
    "No se cuenta con información suficiente en los documentos disponibles para responder "
    "esa consulta. Se recomienda acudir al departamento correspondiente."
)
MAX_FUENTES = 3


@dataclass(frozen=True)
class Fragmento:
    documento: str
    texto: str


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------


class RagNoDisponible(RuntimeError):
    """ChromaDB no está instalado o el índice no existe."""


@lru_cache(maxsize=4)
def _obtener_coleccion(chroma_path: str, nombre: str) -> Any:
    """Abre la colección una sola vez. Si falla, no se guarda en caché y se reintenta."""
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    except ImportError as exc:
        raise RagNoDisponible("chromadb no está instalado") from exc

    if not Path(chroma_path).exists():
        raise RagNoDisponible(
            f"no existe el índice en {chroma_path}; ejecuta: python scripts/indexar.py"
        )

    cliente = chromadb.PersistentClient(path=chroma_path)
    try:
        return cliente.get_collection(name=nombre, embedding_function=DefaultEmbeddingFunction())
    except Exception as exc:
        raise RagNoDisponible(
            f"no existe la colección '{nombre}'; ejecuta: python scripts/indexar.py"
        ) from exc


def recuperar(pregunta: str, limite: int | None = None) -> list[dict[str, Any]]:
    """Devuelve los fragmentos más parecidos a la pregunta con su distancia coseno."""
    coleccion = _obtener_coleccion(str(settings.chroma_path), settings.coleccion)
    resultados = coleccion.query(
        query_texts=[pregunta],
        n_results=limite or settings.n_resultados,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "texto": documento,
            "documento": metadata["documento"],
            "tema": metadata.get("tema", ""),
            "distancia": float(distancia),
        }
        for documento, metadata, distancia in zip(
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
        )
    ]


def _buscar_en_chroma(pregunta: str) -> list[Fragmento]:
    """Filtra por umbral: si nada está suficientemente cerca, no hay evidencia."""
    return [
        Fragmento(documento=r["documento"], texto=r["texto"])
        for r in recuperar(pregunta)
        if r["distancia"] <= settings.umbral_distancia
    ]


# ---------------------------------------------------------------------------
# Respaldo: palabras clave
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "a", "al", "ante", "como", "con", "cual", "cuales", "de", "del", "el", "en", "es",
    "esta", "este", "hay", "la", "las", "lo", "los", "mas", "me", "mi", "o", "para",
    "por", "que", "se", "si", "su", "un", "una", "unas", "unos", "y",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))


def _tokens(texto: str) -> set[str]:
    palabras = re.findall(r"[a-z0-9]+", _normalizar(texto))
    return {p for p in palabras if len(p) > 2 and p not in _STOPWORDS}


def _extraer_fragmentos(contenido: str) -> list[str]:
    fragmentos: list[str] = []
    for bloque in re.split(r"\n\s*\n", contenido.strip()):
        lineas = [ln.strip() for ln in bloque.splitlines() if ln.strip()]
        if not lineas:
            continue
        texto = " ".join(lineas)
        if texto.startswith("# ") or texto.startswith("*Documento ficticio"):
            continue
        fragmentos.append(texto)
    return fragmentos


def cargar_corpus(corpus_path: Path) -> list[Fragmento]:
    if not corpus_path.exists() or not corpus_path.is_dir():
        return []
    fragmentos: list[Fragmento] = []
    for archivo in sorted(corpus_path.glob("*.md")):
        try:
            contenido = archivo.read_text(encoding="utf-8")
        except OSError:
            continue
        for texto in _extraer_fragmentos(contenido):
            fragmentos.append(Fragmento(documento=archivo.name, texto=texto))
    return fragmentos


def buscar_fragmentos(pregunta: str, corpus_path: Path, limite: int = 2) -> list[Fragmento]:
    consulta_tokens = _tokens(pregunta)
    if not consulta_tokens:
        return []
    puntuados: list[tuple[int, int, int, Fragmento]] = []
    for idx, fragmento in enumerate(cargar_corpus(corpus_path)):
        coincidencias = len(consulta_tokens & _tokens(fragmento.texto))
        doc_tokens = _tokens(Path(fragmento.documento).stem.replace("-", " "))
        bono_documento = 2 * len(consulta_tokens & doc_tokens)
        # Evidencia débil (una sola palabra suelta, p. ej. "horario") no cuenta:
        # se exigen 2+ coincidencias o que la pregunta mencione el tema del documento.
        if coincidencias == 0 or (coincidencias < 2 and bono_documento == 0):
            continue
        puntuados.append((coincidencias + bono_documento, coincidencias, -idx, fragmento))
    puntuados.sort(key=lambda t: t[:3], reverse=True)
    return [frag for *_, frag in puntuados[:limite]]


# ---------------------------------------------------------------------------
# Respuesta
# ---------------------------------------------------------------------------


def _resumir(texto: str, max_len: int = 350) -> str:
    limpio = re.sub(r"\s+", " ", texto).strip()
    if len(limpio) <= max_len:
        return limpio
    corte = limpio.rfind(" ", 0, max_len)
    if corte < 200:
        corte = max_len
    return limpio[:corte].rstrip() + "..."


_avisos_mostrados: set[str] = set()


def _avisar_una_vez(clave: str, mensaje: str) -> None:
    """Escribe una advertencia en la consola de uvicorn solo la primera vez."""
    if clave not in _avisos_mostrados:
        logger.warning(mensaje)
        _avisos_mostrados.add(clave)


PROMPT = """Eres TecBot Académico, un asistente de información académica.

Responde en español, de forma breve (máximo 120 palabras), usando únicamente la
información de los FRAGMENTOS.
Si los fragmentos no contienen la respuesta, dilo y recomienda acudir al departamento
correspondiente.
No inventes requisitos, fechas, montos ni enlaces.
Al final de cada afirmación escribe entre corchetes el nombre del archivo de donde
salió, tal como aparece en los FRAGMENTOS (por ejemplo [titulacion.md]).

PREGUNTA:
{pregunta}

FRAGMENTOS:
{contexto}
"""


def _generar_con_ollama(pregunta: str, hallazgos: list[Fragmento]) -> str | None:
    """Pide a Ollama una respuesta basada en los fragmentos. None si no se pudo."""
    if not settings.usar_ollama:
        return None
    try:
        # Importación aquí (no al inicio del archivo): si instalas ollama con el
        # servidor encendido, se detecta en la siguiente pregunta sin reiniciar.
        import ollama
    except ImportError:
        _avisar_una_vez(
            "ollama-paquete",
            "El paquete 'ollama' no está instalado en este entorno (pip install ollama). "
            "Se responde con el resumen del fragmento.",
        )
        return None

    contexto = "\n\n".join(f"[{f.documento}]\n{f.texto}" for f in hallazgos)
    try:
        cliente = ollama.Client(host=settings.ollama_host, timeout=settings.ollama_timeout)
        respuesta = cliente.chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": PROMPT.format(pregunta=pregunta, contexto=contexto)}],
            options={"temperature": 0.1, "num_predict": 400},
            keep_alive="15m",  # mantiene el modelo cargado para que las siguientes sean rápidas
        )
        contenido = respuesta["message"]["content"]
    except Exception as exc:
        logger.warning(
            "Ollama no respondió (%s: %s). ¿Está abierto Ollama y descargado el modelo '%s'? "
            "Se responde con el resumen del fragmento.",
            type(exc).__name__, exc, settings.ollama_model,
        )
        return None

    if isinstance(contenido, str) and contenido.strip():
        return contenido.strip()
    return None


def consultar(pregunta: str, corpus_path: Path | None = None) -> dict[str, Any]:
    try:
        hallazgos = _buscar_en_chroma(pregunta)
    except RagNoDisponible as exc:
        _avisar_una_vez(
            "chroma", f"ChromaDB no disponible ({exc}). Se usa búsqueda por palabras clave."
        )
        hallazgos = buscar_fragmentos(pregunta, corpus_path or settings.corpus_path)
    except Exception:
        logger.exception("Error al consultar ChromaDB. Se usa búsqueda por palabras clave.")
        hallazgos = buscar_fragmentos(pregunta, corpus_path or settings.corpus_path)

    if not hallazgos:
        return {"respuesta": RESPUESTA_SIN_EVIDENCIA, "fuentes": [], "advertencia": ADVERTENCIA}

    hallazgos = hallazgos[:MAX_FUENTES]
    respuesta = _generar_con_ollama(pregunta, hallazgos) or _resumir(hallazgos[0].texto)
    return {
        "respuesta": respuesta,
        "fuentes": [{"documento": f.documento, "fragmento": f.texto} for f in hallazgos],
        "advertencia": ADVERTENCIA,
    }
