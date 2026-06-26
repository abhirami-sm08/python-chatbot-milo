from unittest.mock import Mock, patch

from backend.llm import generate_chat_response


def test_openai_compatible_llm_request_payload():
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Hello from hosted Qwen."
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch("backend.llm.settings.LLM_API_KEY", "test-key"), \
            patch("backend.llm.settings.LLM_BASE_URL", "https://example.test/v1"), \
            patch("backend.llm.settings.LLM_MODEL", "qwen/qwen3-8b"), \
            patch("backend.llm.settings.LLM_PROVIDER", "openai_compatible"), \
            patch("backend.llm.requests.post", return_value=mock_response) as post:

        response = generate_chat_response(
            messages=[
                {
                    "role": "user",
                    "content": "Say hello in one sentence."
                }
            ],
            temperature=0.2,
            max_output_tokens=150
        )

    assert response.text == "Hello from hosted Qwen."
    post.assert_called_once()

    _, kwargs = post.call_args
    assert kwargs["json"]["model"] == "qwen/qwen3-8b"
    assert kwargs["json"]["max_tokens"] == 150
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
