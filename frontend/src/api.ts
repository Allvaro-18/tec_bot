const API_BASE = import.meta.env.VITE_API_URL ?? "";

type ChatResponse = { reply: string };

export async function sendMessage(message: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = (await response.json()) as ChatResponse;
  return data.reply;
}
