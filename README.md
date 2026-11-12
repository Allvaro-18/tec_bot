# TecBot Académico

Asistente de información académica (material didáctico del curso *Creación de software con Agentes de IA*).
FastAPI + ChromaDB + React (Vite + TypeScript).

> Los documentos de `documentos-demo/` son ficticios y no constituyen normativa oficial.

## 1. Instalación (una sola vez)

Desde la **raíz del proyecto** (`tec_bot/`), en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import chromadb; print(chromadb.__version__)"
```

`requirements.txt` instala el backend, las pruebas y `chromadb`.

## 2. Crear el índice de ChromaDB (Día 3)

```powershell
python scripts/indexar.py
```

La primera vez se descarga el modelo de embeddings por defecto (necesita internet una vez).
El índice se guarda en `chroma_db/` (no se versiona).

Si cambias los documentos, `TAMANO` o `SOLAPAMIENTO`, reconstruye el índice:

```powershell
python scripts/indexar.py --reconstruir
```

## 3. Consultar y evaluar la recuperación

```powershell
python scripts/consultar.py                                   # pregunta de ejemplo
python scripts/consultar.py "¿Cuáles son las modalidades de titulación?"
python scripts/consultar.py "¿Cuáles son las modalidades?" --tema titulacion   # filtro por metadatos
python scripts/consultar.py --evaluar                         # tabla: documento, top-3, distancia
```

`--evaluar` corre las 5 preguntas de ejemplo de `requerimientos.md` y sugiere un **umbral de distancia**.
Cópialo a `backend/.env`:

```
TECBOT_UMBRAL_DISTANCIA=0.5
```

La API solo acepta como evidencia los fragmentos con distancia menor o igual al umbral; si ninguno pasa, responde
que no hay información suficiente.

Opcional, generar una respuesta con un modelo local (Paso 4):

```powershell
pip install ollama
ollama pull llama3.2:3b
python scripts/responder.py "¿Qué necesito para iniciar el servicio social?"
```

## 4. Backend

```powershell
cd backend
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Documentación: http://localhost:8000/docs
- `GET /salud` y `POST /consultas` con `{"pregunta": "..."}` → `{respuesta, fuentes, advertencia}`.
- Si ChromaDB no está instalado o el índice no existe, la API usa una búsqueda por palabras clave como respaldo
  y lo avisa en la consola.

Pruebas:

```powershell
cd backend
pytest -q
```

`tests/test_rag_chroma.py` construye un índice temporal y verifica que una pregunta de servicio social recupere
`servicio-social.md`.

## 5. Frontend

```powershell
cd frontend
npm install
npm run dev
```

http://localhost:5173. Vite reenvía `/api/*` al backend en el puerto 8000.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `ModuleNotFoundError: chromadb` | Activa `.venv` de la raíz y ejecuta `pip install -r requirements.txt`. |
| La primera consulta tarda mucho | Se está descargando el modelo de embeddings. |
| Resultados duplicados o viejos | `python scripts/indexar.py --reconstruir`. |
| La cafetería devuelve fuentes | Baja `TECBOT_UMBRAL_DISTANCIA` según `consultar.py --evaluar`. |
| Una pregunta válida dice "sin información" | Sube `TECBOT_UMBRAL_DISTANCIA`. |
