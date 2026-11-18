import pytest
from unittest.mock import Mock

from src.ai.agents.tool import AgentTool
from src.ai.agents.generation_agent import GenerationAgent
from src.ai.agents.tool_call import ToolCall
from src.ai.agents.tool_registry import ToolRegistry
from src.data_models.generation_request import GenerationRequest
from src.data_models.generation_complexity import GenerationComplexity
from src.printers.printer_profile import PrinterProfile

@pytest.fixture
def tool_registry():
    return ToolRegistry()

@pytest.fixture
def beam_tool():
    def generate_beam(arguments):
        return "Beam generated"

    return AgentTool(
        name="beam_generator",
        description="Generates a beam.",
        function=generate_beam,
    )

@pytest.fixture
def valid_request():
    return GenerationRequest(
        prompt="Create a beam",
        complexity=GenerationComplexity.MEDIUM,
        printer_profile=Mock(spec=PrinterProfile),
    )

def select_beam_tool(request, available_tools):
    return ToolCall(
        tool_name="beam_generator",
        arguments={},
    )

def select_unknown_tool(request, available_tools):
    return ToolCall(
        tool_name="unknown_tool",
        arguments={},
    )

def invalid_decision(request, available_tools):
    return {}

def test_run_executes_selected_tool(
        tool_registry,
        beam_tool,
        valid_request,
):
    tool_registry.register(beam_tool)

    agent = GenerationAgent(
        tool_registry=tool_registry,
        decision_function=select_beam_tool,
    )

    result = agent.run(valid_request)

    assert result == "Beam generated"

def test_error_for_unknown_tool(
        tool_registry,
        beam_tool,
        valid_request,
):
    tool_registry.register(beam_tool)

    agent = GenerationAgent(
        tool_registry=tool_registry,
        decision_function=select_unknown_tool,
    )

    with pytest.raises(ValueError, match="not registered"):
        agent.run(valid_request)

def test_run_for_invalid_tool_call(
        tool_registry,
        beam_tool,
        valid_request,
):
    tool_registry.register(beam_tool)

    agent = GenerationAgent(
        tool_registry=tool_registry,
        decision_function=invalid_decision,
    )

    with pytest.raises(TypeError, match="Decision function must return a ToolCall.",):
        agent.run(valid_request)


def test_run_error_when_no_tools_registered(
        tool_registry,
        valid_request,
):
    agent = GenerationAgent(
        tool_registry=tool_registry,
        decision_function=select_beam_tool,
    )

    with pytest.raises(RuntimeError, match="No tools are registered"):
        agent.run(valid_request)


