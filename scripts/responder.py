"""(Opcional) Genera una respuesta con fuentes usando Ollama (Día 3 · Paso 4).

Requiere:  pip install ollama   y   ollama pull llama3.2:3b

Uso:
    python scripts/responder.py "¿Qué necesito para iniciar el servicio social?"
"""

from __future__ import annotations

import sys

import ollama

from consultar import PREGUNTA, buscar, obtener_coleccion

MODELO = "llama3.2:3b"


def main() -> None:
    pregunta = sys.argv[1] if len(sys.argv) > 1 else PREGUNTA
    resultados = buscar(obtener_coleccion(), pregunta, n=4)

    contexto = "\n\n".join(f"[{r['documento']}]\n{r['texto']}" for r in resultados)
    prompt = f"""Eres un asistente de información académica.

Responde únicamente con la información de los FRAGMENTOS.
Si no hay información suficiente, dilo y recomienda acudir al departamento correspondiente.
No inventes requisitos, fechas, montos ni enlaces.
Cita el documento de cada afirmación con el formato [documento].

PREGUNTA:
{pregunta}

FRAGMENTOS:
{contexto}
"""
    respuesta = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}])
    print(respuesta["message"]["content"])
    print("\nFuentes recuperadas:")
    for r in resultados:
        print(f"- {r['documento']} (distancia {r['distancia']:.3f})")


if __name__ == "__main__":
    main()
