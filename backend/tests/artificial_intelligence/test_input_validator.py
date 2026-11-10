import pytest
from unittest.mock import Mock

from src.artificial_intelligence.input_validator import (
    validate_generation_request,
)
from src.data_models.generation_complexity import GenerationComplexity
from src.data_models.generation_request import GenerationRequest
from src.printers.printer_profile import PrinterProfile


@pytest.fixture
def valid_request():
    return GenerationRequest(
        prompt="Create a LEGO robot",
        complexity=GenerationComplexity.MEDIUM,
        printer_profile=Mock(spec=PrinterProfile),
    )

def test_valid_generation_request(valid_request):
    assert validate_generation_request(valid_request) is None

def test_request_cannot_be_empty():
    with pytest.raises(TypeError, match="Invalid generation request."):
        validate_generation_request(None)


@pytest.mark.parametrize("prompt", [
    "",
    "   ",
    "\n\t",
])
def test_prompt_cannot_be_empty(valid_request, prompt):
    valid_request.prompt = prompt

    with pytest.raises(ValueError, match="cannot be empty."):
        validate_generation_request(valid_request)

def test_prompt_cannot_short(valid_request):
    valid_request.prompt = "a"

    with pytest.raises(ValueError, match="too short."):
        validate_generation_request(valid_request)

def test_prompt_cannot_long(valid_request):
    valid_request.prompt = "a" * 1001

    with pytest.raises(ValueError, match="Prompt is too long."):
        validate_generation_request(valid_request)

def test_prompt_must_be_string(valid_request):
    valid_request.prompt = 123

    with pytest.raises(TypeError, match="must be a string"):
        validate_generation_request(valid_request)

@pytest.mark.parametrize("complexity", [
    "low",
    "medium",
    "high",
    None,
    True,
])
def test_complexity_must_be_enum(complexity, valid_request):
    valid_request.complexity = complexity

    with pytest.raises(ValueError, match="Invalid generation complexity."):
        validate_generation_request(valid_request)

