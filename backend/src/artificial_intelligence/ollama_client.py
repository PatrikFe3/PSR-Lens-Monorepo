import os
from typing import Any

from dotenv import load_dotenv
from ollama import Client
from ollama import ResponseError
from httpx import HTTPError

from src.exceptions.ollama_exception import OllamaConnectionError

load_dotenv()

class OllamaClient:

    def __init__(
            self,
    ):
        host = os.getenv("OLLAMA_HOST")
        model = os.getenv("OLLAMA_MODEL")
        timeout = float(os.getenv("OLLAMA_TIMEOUT"))

        self._client = Client(host=host, timeout=timeout)
        self._model = model

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

        except HTTPError as err:
            raise OllamaConnectionError("Could not communicate with Ollama.") from err

        except ResponseError as err:
            raise OllamaConnectionError("Ollama returned an error while generating a response.") from err

