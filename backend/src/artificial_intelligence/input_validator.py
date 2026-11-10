from src.data_models.generation_request import GenerationRequest
from src.data_models.generation_complexity import GenerationComplexity

MAX_PROMPT_LENGTH = 1000
MIN_PROMPT_LENGTH = 3

def validate_generation_request(request: GenerationRequest) -> None:

    if not isinstance(request, GenerationRequest):
        raise TypeError("Invalid generation request.")

    prompt = request.prompt

    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")

    prompt = prompt.strip()

    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError("Prompt is too long.")

    if len(prompt) < MIN_PROMPT_LENGTH:
        raise ValueError("Prompt is too short.")

    if not isinstance(request.complexity, GenerationComplexity):
        raise ValueError("Invalid generation complexity.")