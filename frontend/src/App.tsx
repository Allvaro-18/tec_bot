import { useState, type FormEvent } from "react";

import { enviarConsulta, type ConsultaResponse } from "./api";

const MAX_CARACTERES = 1000;

export default function App() {
  const [pregunta, setPregunta] = useState("");
  const [resultado, setResultado] = useState<ConsultaResponse | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const texto = pregunta.trim();
    if (!texto) {
      setError("Escribe una pregunta.");
      return;
    }

    setCargando(true);
    setError("");
    setResultado(null);
    try {
      setResultado(await enviarConsulta(texto));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setCargando(false);
    }
  }

  return (
    <main>
      <h1>TecBot Académico</h1>
      <p className="aviso" role="note">
        Material didáctico: las respuestas provienen de documentos ficticios de demostración y no
        constituyen normativa oficial.
      </p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="pregunta" className="sr-only">
          Pregunta
        </label>
        <input
          id="pregunta"
          value={pregunta}
          maxLength={MAX_CARACTERES}
          onChange={(event) => setPregunta(event.target.value)}
          placeholder="Ej. ¿Qué necesito para el servicio social?"
        />
        <button type="submit" disabled={cargando}>
          {cargando ? "Buscando..." : "Preguntar"}
        </button>
      </form>

      {cargando && <p aria-live="polite">Consultando los documentos...</p>}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {resultado && (
        <section className="resultado" aria-live="polite">
          <p>{resultado.respuesta}</p>

          {resultado.fuentes.length > 0 && (
            <>
              <h2>Fuentes</h2>
              <ul>
                {resultado.fuentes.map((fuente, i) => (
                  <li key={`${fuente.documento}-${i}`}>
                    <details>
                      <summary>{fuente.documento}</summary>
                      <p className="fragmento">{fuente.fragmento}</p>
                    </details>
                  </li>
                ))}
              </ul>
            </>
          )}

          <p className="advertencia">{resultado.advertencia}</p>
        </section>
      )}
    </main>
  );
}
