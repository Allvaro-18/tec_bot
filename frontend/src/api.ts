const API_BASE = import.meta.env.VITE_API_URL ?? "";

export type Fuente = { documento: string; fragmento: string };

export type ConsultaResponse = {
  respuesta: string;
  fuentes: Fuente[];
  advertencia: string;
};

export async function enviarConsulta(pregunta: string): Promise<ConsultaResponse> {
  // En desarrollo, Vite reenvía /api/* al backend quitando el prefijo /api.
  const base = API_BASE || "/api";
  const response = await fetch(`${base}/consultas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pregunta }),
  });

  if (response.status === 422) {
    throw new Error("La pregunta no puede estar vacía ni superar 1,000 caracteres.");
  }
  if (!response.ok) {
    throw new Error(`Error del servidor (${response.status}). Intenta de nuevo.`);
  }

  return (await response.json()) as ConsultaResponse;
}
