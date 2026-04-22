export interface ChatResponse {
  session_id: string;
  reply: string;
  intent: string;
  lead_captured: boolean;
}

export const sendMessage = async (
  message: string, 
  sessionId: string = "default-session",
  token: string | null = null
): Promise<ChatResponse> => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers,
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to communicate with the Agent API");
  }

  return response.json();
};
