"""Indexa los documentos de demostración en ChromaDB (Día 3 · Paso 1).

Uso (desde la raíz del proyecto, con el entorno virtual activo):

    python scripts/indexar.py
    python scripts/indexar.py --reconstruir   # borra la colección y la vuelve a crear

Las rutas se calculan a partir de la ubicación de este archivo, así que el script
funciona aunque lo ejecutes desde otra carpeta.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

RAIZ = Path(__file__).resolve().parents[1]
DOCUMENTOS = RAIZ / "documentos-demo"
CHROMA_PATH = RAIZ / "chroma_db"
COLECCION = "documentos_academicos"
TAMANO = 800
SOLAPAMIENTO = 120


def dividir_texto(
    texto: str, tamano: int = TAMANO, solapamiento: int = SOLAPAMIENTO
) -> list[str]:
    """Divide por párrafos y agrupa hasta alcanzar el tamaño objetivo."""
    parrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    fragmentos: list[str] = []
    actual = ""

    for parrafo in parrafos:
        if len(actual) + len(parrafo) + 2 <= tamano:
            actual = f"{actual}\n\n{parrafo}".strip()
            continue

        if actual:
            fragmentos.append(actual)
            # Conserva el final del fragmento anterior como contexto.
            actual = f"{actual[-solapamiento:]}\n\n{parrafo}".strip()
        else:
            fragmentos.append(parrafo)
            actual = ""

    if actual:
        fragmentos.append(actual)

    return fragmentos


def preparar_fragmentos(
    documentos_dir: Path,
) -> tuple[list[str], list[str], list[dict]]:
    """Lee los .md y devuelve ids, textos y metadatos listos para ChromaDB."""
    ids: list[str] = []
    documentos: list[str] = []
    metadatos: list[dict] = []

    for ruta in sorted(documentos_dir.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        tema = ruta.stem
        for indice, fragmento in enumerate(dividir_texto(texto)):
            ids.append(f"{tema}-{indice:03d}")
            documentos.append(fragmento)
            metadatos.append(
                {
                    "documento": ruta.name,
                    "tema": tema,
                    "fragmento": indice,
                    "tipo": "demostracion",
                }
            )

    return ids, documentos, metadatos


def indexar(
    documentos_dir: Path = DOCUMENTOS,
    chroma_path: Path = CHROMA_PATH,
    nombre_coleccion: str = COLECCION,
    reconstruir: bool = False,
) -> int:
    """Crea (o actualiza) la colección y devuelve el total de fragmentos."""
    ids, documentos, metadatos = preparar_fragmentos(documentos_dir)
    if not ids:
        raise SystemExit(f"No se encontraron documentos para indexar en {documentos_dir}")

    cliente = chromadb.PersistentClient(path=str(chroma_path))

    if reconstruir:
        # Si cambiaste TAMANO o SOLAPAMIENTO, los ids viejos quedarían "huérfanos";
        # borrar la colección evita resultados duplicados o desactualizados.
        try:
            cliente.delete_collection(nombre_coleccion)
            print(f"Colección anterior '{nombre_coleccion}' eliminada.")
        except Exception:
            pass

    coleccion = cliente.get_or_create_collection(
        name=nombre_coleccion,
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )
    coleccion.upsert(ids=ids, documents=documentos, metadatas=metadatos)

    print(f"Documentos indexados: {len(ids)}")
    print(f"Colección: {coleccion.name}")
    print(f"Total en la colección: {coleccion.count()}")
    print(f"Ubicación del índice: {chroma_path}")
    return coleccion.count()


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexa documentos-demo/ en ChromaDB.")
    parser.add_argument(
        "--reconstruir",
        action="store_true",
        help="Borra la colección antes de indexar (úsalo si cambiaste la fragmentación).",
    )
    args = parser.parse_args()
    indexar(reconstruir=args.reconstruir)


if __name__ == "__main__":
    main()
