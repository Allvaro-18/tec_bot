# AGENTS.md — TecBot Académico

## Propósito

Asistente de información académica para estudiantes del ITS Santiago Papasquiaro.
Responde preguntas sobre servicio social, residencias, titulación y acreditación
usando únicamente los documentos de `documentos-demo/`.

## Alcance

Incluye:
- Consultas en lenguaje natural.
- Recuperación de fragmentos documentales.
- Respuestas con fuentes.
- Derivación al departamento cuando no hay evidencia.

No incluye:
- Autenticación de usuarios.
- Trámites oficiales ni firmas.
- Datos personales.
- Normativa institucional real.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- ChromaDB
- OpenCode
- Git y GitHub
- Frontend estático (HTML/CSS/JS o React)

## Estructura

- `backend/app/` — API y lógica de recuperación.
- `backend/app/main.py` — entrada de FastAPI.
- `backend/app/services/rag.py` — consulta a ChromaDB (`recuperar()`) y respaldo por palabras clave.
- `scripts/indexar.py` — fragmenta `documentos-demo/` y crea la colección `documentos_academicos`.
- `scripts/consultar.py` — consulta por similitud y evalúa la recuperación (`--evaluar`).
- `chroma_db/` — índice generado; no se versiona.
- `documentos-demo/` — corpus ficticio de demostración.
- `documentacion/` — requerimientos, arquitectura y pruebas.
- `prompts/` — instrucciones de subagentes.
- `tests/` — pruebas automatizadas.

## Comandos

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/indexar.py
cd backend
uvicorn app.main:app --reload
pytest -q
```

## Reglas

1. No inventar requisitos, fechas, montos ni enlaces.
2. Toda respuesta debe citar al menos un documento de `documentos-demo/`.
3. Si la recuperación no encuentra evidencia suficiente, responder que no se
   cuenta con información y recomendar acudir al departamento correspondiente.
4. No modificar `documentos-demo/` para “hacer que una respuesta funcione”.
5. No agregar dependencias sin justificar el motivo y actualizar requirements.txt.
6. No incluir credenciales, tokens ni datos personales en el repositorio.
7. Los documentos son material didáctico; nunca presentarlos como normativa oficial.

## Convenciones

- Python con type hints en funciones públicas.
- Nombres de archivos en snake_case.
- Rutas de API en español y en plural cuando representan recursos.
- Respuestas JSON con las claves `respuesta`, `fuentes` y `advertencia`.
- Mensajes de commit en formato Conventional Commits.

## Definición de terminado

Una tarea está terminada cuando:
- El código compila y las pruebas pasan.
- Existe al menos una prueba para el caso feliz y una para el caso sin evidencia.
- Se actualizó la documentación afectada.
- El cambio fue revisado con `git diff`.

# Equipo de agentes — TecBot Académico

## Coordinador (agente principal)
- Lee requerimientos y arquitectura.
- Descompone tareas.
- Delega a subagentes.
- Revisa e integra.
- Ejecuta o solicita pruebas.

## Arquitecto
- Analiza requerimientos.
- Define estructura y contratos de API.
- Documenta decisiones.
- Revisa coherencia backend/frontend.

## Diseñador web
- Define sistema de diseño.
- Diseña componentes y pantallas.
- Garantiza accesibilidad y responsive.
- Trabaja con design.md.

## Desarrollador
- Implementa endpoints y componentes.
- Integra frontend/backend.
- Mantiene buenas prácticas.

## Tester
- Diseña y ejecuta pruebas.
- Reporta defectos.
- Verifica correcciones.