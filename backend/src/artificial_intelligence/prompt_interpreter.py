# Understands the request. He handles communication with the AI
import json

from src.artificial_intelligence.ollama_client import OllamaClient

from src.schemas.assembly_plan_schema import (
    ASSEMBLY_PLAN_SCHEMA
)

from src.data_models.generation_request import GenerationRequest
from src.data_models.prompt_interpretation import PromptInterpretation

from src.data_models.assembly_plan import AssemblyInstruction, AssemblyPlan


class PromptInterpreter:

    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client

    def interpret(
            self,
            request: GenerationRequest
    ) -> PromptInterpretation:

        prompt = self._build_prompt(request)

        response = self.ollama_client.generate(
            prompt=prompt,
            response_format=ASSEMBLY_PLAN_SCHEMA
        )

        return self._parse_response(response)

    def _build_prompt(self, request: GenerationRequest) -> str:

        return f"""
You are an AI assistant responsible for planning 3D printable
parametric assemblies.

Your task is to interpret the user's request and create
a structured assembly plan.

User request:
{request.prompt}

Requested complexity:
{request.complexity.value}

Available component types:
- brick_1x1
- brick_2x1
- brick_2x2
- brick_4x2
- brick_4x4
- brick_6x2

Rules:
1. Use only the available component types.
2. Every component must have a unique component_id.
3. The first component must have parent_id = null
   and attachment = null.
4. Every other component must reference an existing parent.
5. Use "top" as attachment when placing a component above its parent.
6. Keep the assembly appropriate for the requested complexity.
7. Create a plan that can be assembled from the available components.
8. Return only data matching the provided JSON schema.
        """

    def _parse_response(
            self,
            response: str,
    ) -> PromptInterpretation:

        try:
            data = json.loads(response)

            assembly_data = data["assembly_plan"]

            instructions = [
                AssemblyInstruction(
                    component_id=item["component_id"],
                    component_type=item["component_type"],
                    parent_id=item["parent_id"],
                    attachment=["attachment"]
                )
                for item in assembly_data["instructions"]
            ]

            assembly_plan = AssemblyPlan(
                name=assembly_data["name"],
                instructions=instructions,
            )

            return PromptInterpretation(
                object_type=data["object_type"],
                assembly_plan=assembly_plan,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ValueError(
                "AI returned an invalid assembly plan."
            ) from error