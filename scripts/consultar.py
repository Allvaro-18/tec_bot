import chromadb
import ollama
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

PREGUNTA = "¿Qué necesito para iniciar el servicio social?"
MODELO = "llama3.2:3b"

cliente = chromadb.PersistentClient(path="chroma_db")
coleccion = cliente.get_collection(
    name="documentos_academicos",
    embedding_function=DefaultEmbeddingFunction(),
)

resultados = coleccion.query(
    query_texts=[PREGUNTA],
    n_results=4,
    include=["documents", "metadatas", "distances"],
)

fragmentos = resultados["documents"][0]
metadatos = resultados["metadatas"][0]
contexto = "\n\n".join(
    f"[{meta['documento']}]\n{doc}" for doc, meta in zip(fragmentos, metadatos)
)

prompt = f"""Eres un asistente de información académica.

Responde únicamente con la información de los FRAGMENTOS.
Si no hay información suficiente, dilo y recomienda acudir al departamento correspondiente.
No inventes requisitos, fechas, montos ni enlaces.
Cita el documento de cada afirmación con el formato [documento].

PREGUNTA:
{PREGUNTA}

FRAGMENTOS:
{contexto}
"""

respuesta = ollama.chat(
    model=MODELO,
    messages=[{"role": "user", "content": prompt}],
)

print(respuesta["message"]["content"])
print("\nFuentes recuperadas:")
for meta in metadatos:
    print(f"- {meta['documento']}")