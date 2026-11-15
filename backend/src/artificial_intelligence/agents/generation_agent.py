# Orchestrator of the whole decision system
from collections.abc import Callable
from typing import Any

from src.artificial_intelligence.prompt_interpreter import PromptInterpreter
from src.assembly.spatial_planner import plan_spatial_layout
from src.services.assembly_service import generate_assembly
from src.artificial_intelligence.agents.tool import AgentTool
from src.artificial_intelligence.agents.tool_call import ToolCall
from src.artificial_intelligence.agents.tool_registry import ToolRegistry
from src.data_models.generation_request import GenerationRequest
from src.artificial_intelligence.input_validator import (
    validate_generation_request,
)

ToolDecisionFunction = Callable[
    [GenerationRequest, list[AgentTool]],
    ToolCall,
]

class GenerationAgent:

    def __init__(
            self,
            tool_registry: ToolRegistry,
            decision_function: ToolDecisionFunction,
            prompt_interpreter: PromptInterpreter,
    ):
        self._tool_registry = tool_registry
        self._decision_function = decision_function
        self._prompt_interpreter = prompt_interpreter

    def run(self, request: GenerationRequest) -> Any:

        validate_generation_request(request)

        available_tools = self._tool_registry.get_available_tools()

        if not available_tools:
            raise RuntimeError("No tools are registered.")

        tool_call = self._decision_function(
            request,
            available_tools,
        )

        if not isinstance(tool_call, ToolCall):
            raise TypeError("Decision function must return a ToolCall.")

        tool = self._tool_registry.get_tool(tool_call.tool_name)

        return tool.execute(tool_call.arguments)

    def generate(self, request: GenerationRequest):
        validate_generation_request(request)

        interpretation = self._prompt_interpreter.interpret(request)

        if interpretation.object_type == "assembly_plan":
            components = plan_spatial_layout(
                interpretation.assembly_plan,
            )

            return generate_assembly(components)
        raise ValueError(
            f"Unsupported object type: {interpretation.object_type}"
        )