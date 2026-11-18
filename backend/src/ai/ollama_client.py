from typing import Any

from httpx import HTTPError
from ollama import Client, ResponseError

from src.core.settings import get_settings
from src.exceptions.ollama_exception import OllamaConnectionError


class OllamaClient:

    def __init__(self, host: str | None = None, model: str | None = None, timeout: float | None = None):
        settings = get_settings()
        self._client = Client(host=host or settings.ollama_host,
                              timeout=timeout if timeout is not None else settings.ollama_timeout)
        self._model = model or settings.ollama_model

    def generate(
            self,
            prompt: str,
            response_format: dict[str, Any] | str = "json",
    ) -> str:

        try:
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
                },
            )
            return response.message.content

        except (HTTPError, ConnectionError) as err:
            raise OllamaConnectionError("Could not communicate with Ollama. Is 'ollama serve' running?") from err

        except ResponseError as err:
            raise OllamaConnectionError(f"Ollama returned an error while generating a response: {err}") from err

