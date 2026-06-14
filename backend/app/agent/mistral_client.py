from mistralai import Mistral
from flask import current_app


def get_mistral_client() -> Mistral:
    """Return an authenticated Mistral client."""
    api_key = current_app.config["MISTRAL_API_KEY"]
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set")
    return Mistral(api_key=api_key)


def chat_completion(messages: list[dict]) -> str:
    """
    Send a list of messages to Mistral and return the assistant reply.
    messages format: [{"role": "user", "content": "..."}]
    """
    client = get_mistral_client()
    model = current_app.config["MISTRAL_MODEL"]

    response = client.chat.complete(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content
