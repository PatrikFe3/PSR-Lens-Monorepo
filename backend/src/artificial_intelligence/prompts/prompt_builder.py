# Rules for assembling the final prompt from individual ones.
from src.artificial_intelligence.prompts.retry_prompt import RETRY_RULES
from src.artificial_intelligence.prompts.assembly_prompt import ASSEMBLY_RULES
from src.artificial_intelligence.prompts.base_prompt import BASE_RULES
from src.data_models.generation_request import GenerationRequest


def build_assembly_prompt(request: GenerationRequest) -> str:
    return f"""
{BASE_RULES}

{ASSEMBLY_RULES}

User request:
{request.prompt}

Requested complexity:
{request.complexity.value}
"""

def build_retry_prompt(
        original_prompt: str,
        previous_response: str,
        validation_error: str,
) -> str:

    return f"""
{original_prompt}

{RETRY_RULES}

Previous AI response:
{previous_response}

Validation error:
{validation_error}
"""