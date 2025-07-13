export async function queryLLM(question) {
  const response = await fetch("http://localhost:8000/api/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch answer");
  }

  return response.json();
}
