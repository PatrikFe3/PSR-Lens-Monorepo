import pytest

from src.ai.agents.tool import AgentTool
from src.ai.agents.tool_registry import ToolRegistry


@pytest.fixture
def registry():
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

def test_register_tool(registry, beam_tool):
    registry.register(beam_tool)

    assert registry.get_tool("beam_generator") is beam_tool

def test_register_duplicate_tool(registry, beam_tool):
    registry.register(beam_tool)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(beam_tool)

def test_get_unregistered_tool(registry):
    with pytest.raises(ValueError, match="not registered"):
        registry.get_tool("unknown_tool")

def test_get_available_tools(registry, beam_tool):
    registry.register(beam_tool)

    tools = registry.get_available_tools()

    assert len(tools) == 1
    assert tools[0] is beam_tool

def test_execute_tool(beam_tool):
    result = beam_tool.execute({})

    assert result == "Beam generated"