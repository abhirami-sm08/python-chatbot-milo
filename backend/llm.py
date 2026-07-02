import re
import json
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

def _strip_think_tags(text: str) -> str:
    """Remove qwen3 <think>...</think> reasoning blocks from output."""
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def generate_chat_response_stream(
    messages,
    temperature: float = 0.1,
    max_output_tokens: int = 120,
    model=None
):
    """
    Generator that yields text tokens as they arrive from the LLM.
    Supports both Ollama (local) and OpenAI-compatible (OpenRouter) providers.
    """
    if settings.LLM_PROVIDER == "ollama":
        yield from _stream_with_ollama(messages, temperature, max_output_tokens, model)
    else:
        yield from _stream_with_openai_compatible_stream(messages, temperature, max_output_tokens, model)


def _stream_with_ollama(
    messages,
    temperature: float,
    max_output_tokens: int,
    model
):
    """Stream tokens from a local Ollama instance (qwen3:8b)."""
    payload = {
        "model": model or settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": True,                  # ← real token streaming
        "options": {
            "temperature": temperature,
            "num_predict": max_output_tokens,
            "think": False,              # ← disable qwen3 thinking mode for speed
        },
    }

    try:
        with requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            stream=True,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        ) as resp:
            resp.raise_for_status()
            pending = ""
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                try:
                    data = json.loads(raw_line.decode("utf-8"))
                    token = data.get("message", {}).get("content", "")
                    if token:
                        # Accumulate to strip any stray <think> fragments
                        pending += token
                        # Flush complete tokens (not inside a think block)
                        if "<think>" not in pending:
                            clean = _strip_think_tags(pending)
                            if clean:
                                yield clean
                            pending = ""
                        elif "</think>" in pending:
                            # think block closed — strip it and flush
                            pending = _strip_think_tags(pending)
                            if pending:
                                yield pending
                            pending = ""
                    if data.get("done"):
                        # Flush any remainder
                        if pending:
                            clean = _strip_think_tags(pending)
                            if clean:
                                yield clean
                        break
                except Exception:
                    pass
    except Exception as e:
        print(f"Ollama stream error: {e}")
        yield "Sorry, I\'m having trouble connecting right now."


def _stream_with_openai_compatible_stream(
    messages,
    temperature: float,
    max_output_tokens: int,
    model
):
    """Stream tokens from an OpenAI-compatible API (e.g. OpenRouter)."""
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not set in backend/.env")

    payload = {
        "model": model or settings.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_output_tokens,
        "stream": True,                  # ← real token streaming
    }
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with requests.post(
            f"{settings.LLM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            stream=True,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8")
                if not line.startswith("data: "):
                    continue
                chunk = line[6:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    token = (
                        data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    if token:
                        yield _strip_think_tags(token) if ("<" in token) else token
                except Exception:
                    pass
    except Exception as e:
        print(f"OpenAI-compatible stream error: {e}")
        yield "Sorry, I\'m having trouble connecting right now."
