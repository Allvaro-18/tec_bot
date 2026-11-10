import { useState, type FormEvent } from "react";

import { sendMessage } from "./api";

export default function App() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError("");
    try {
      setReply(await sendMessage(message.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>TEC Bot</h1>
      <form onSubmit={handleSubmit}>
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Escribe un mensaje"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Enviando..." : "Enviar"}
        </button>
      </form>
      {reply && <p>Respuesta: {reply}</p>}
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
