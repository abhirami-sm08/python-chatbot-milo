import requests

from backend.config import settings


class LLMResponse:
    def __init__(self, text: str):
        self.text = text


def generate_chat_response(
    messages,
    temperature=0.2,
    max_output_tokens=None,
    model=None
):
    """
    Generate a chat response using either a hosted OpenAI-compatible API
    or optional local Ollama fallback.
    """
    if settings.LLM_PROVIDER == "ollama":
        return _generate_with_ollama(
            messages,
            temperature,
            max_output_tokens,
            model
        )

    return _generate_with_openai_compatible(
        messages,
        temperature,
        max_output_tokens,
        model
    )


def generate(prompt: str) -> str:
    response = generate_chat_response(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.text


def _generate_with_openai_compatible(
    messages,
    temperature,
    max_output_tokens,
    model
):
    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not set. Add it to backend/.env before using "
            "the hosted LLM provider."
        )

    payload = {
        "model": model or settings.LLM_MODEL,
        "messages": messages,
        "temperature": temperature
    }

    if max_output_tokens:
        payload["max_tokens"] = max_output_tokens

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{settings.LLM_BASE_URL}/chat/completions",
        json=payload,
        headers=headers,
        timeout=settings.LLM_TIMEOUT_SECONDS
    )
    response.raise_for_status()

    data = response.json()
    text = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    return LLMResponse(text)


def _generate_with_ollama(
    messages,
    temperature,
    max_output_tokens,
    model
):
    payload = {
        "model": model or settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    if max_output_tokens:
        payload["options"]["num_predict"] = max_output_tokens

    response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=settings.LLM_TIMEOUT_SECONDS
    )
    response.raise_for_status()

    data = response.json()
    text = data.get("message", {}).get("content", "")

    return LLMResponse(text)
