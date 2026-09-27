import httpx
from app.config import settings


async def complete(
    client: httpx.AsyncClient,
    prompt: str,
    system: str = "",
    max_tokens: int = 1024,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await client.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.llm_model,
            "messages": messages,
            "max_tokens": max_tokens,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
