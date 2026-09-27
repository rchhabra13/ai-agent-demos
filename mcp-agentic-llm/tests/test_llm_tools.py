import pytest
import respx
import httpx

from app.integrations.llm_client import complete
from app.config import settings


@pytest.mark.asyncio
async def test_complete_success():
    with respx.mock:
        url = f"{settings.llm_base_url}/chat/completions"
        respx.post(url).mock(
            return_value=httpx.Response(200, json={
                "choices": [{"message": {"role": "assistant", "content": "Hello from LLM!"}}]
            })
        )
        async with httpx.AsyncClient() as client:
            result = await complete(client, prompt="Say hello", system="You are helpful", max_tokens=50)
        assert result == "Hello from LLM!"


@pytest.mark.asyncio
async def test_complete_no_system():
    with respx.mock:
        url = f"{settings.llm_base_url}/chat/completions"
        respx.post(url).mock(
            return_value=httpx.Response(200, json={
                "choices": [{"message": {"role": "assistant", "content": "No system"}}]
            })
        )
        async with httpx.AsyncClient() as client:
            result = await complete(client, prompt="Hi")
        assert "No system" in result


@pytest.mark.asyncio
async def test_complete_api_error():
    with respx.mock:
        url = f"{settings.llm_base_url}/chat/completions"
        respx.post(url).mock(return_value=httpx.Response(401, json={"error": "Unauthorized"}))
        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await complete(client, prompt="test")
