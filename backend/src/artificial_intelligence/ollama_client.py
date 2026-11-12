from typing import Any

from ollama import Client

class OllamaClient:

    def __init__(
            self,
            model: str = "qwen3:4b-instruct",
            host: str = "http://localhost:11434",
    ):
        self._client = Client(host=host)
        self._model = model

    def generate(
            self,
            prompt: str,
            response_format: dict[str, Any] | str = "json",
    ) -> str:
        response = self._client.chat(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format=response_format,
            options={
                "temperature": 0
            }
        )

        return response.message.content