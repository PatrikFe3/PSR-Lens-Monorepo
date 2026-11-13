# Understands the request. He handles communication with the AI
import json

from src.artificial_intelligence.prompts import prompt_builder
from src.artificial_intelligence.ollama_client import OllamaClient

from src.schemas.assembly_plan_schema import (
    ASSEMBLY_PLAN_SCHEMA
)

from src.data_models.generation_request import GenerationRequest
from src.data_models.prompt_interpretation import PromptInterpretation

from src.data_models.assembly_plan import AssemblyInstruction, AssemblyPlan
from src.assembly.assembly_plan_validator import validate_assembly_plan


class PromptInterpreter:

    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client

    def interpret(
            self,
            request: GenerationRequest
    ) -> PromptInterpretation:

        original_prompt = self._build_prompt(request)
        prompt = original_prompt

        last_error = None

        for attempt in range(2):
            response = self.ollama_client.generate(
                prompt=prompt,
                response_format=ASSEMBLY_PLAN_SCHEMA
            )

            print("\n--- RAW AI RESPONSE ---")
            print(response)
            print("--- END RAW RESPONSE ---")

            try:
                return self._parse_response(response)
            except ValueError as error:
                last_error = error
                if attempt < 1:
                    prompt = prompt_builder.build_retry_prompt(
                        original_prompt=original_prompt,
                        previous_response=response,
                        validation_error=str(error)
                    )

        raise ValueError(
            "AI could not generate a valid assembly plan."
        ) from last_error

    def _build_prompt(self, request: GenerationRequest) -> str:
        return prompt_builder.build_assembly_prompt(request)

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
                    attachment=(
                        None
                        if item["parent_id"] is None
                        else item["attachment"]
                    )
                )
                for item in assembly_data["instructions"]
            ]

            assembly_plan = AssemblyPlan(
                name=assembly_data["name"],
                instructions=instructions,
            )

            validate_assembly_plan(assembly_plan)

            return PromptInterpretation(
                object_type=data["object_type"],
                assembly_plan=assembly_plan,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ValueError(
                "AI returned an invalid assembly plan."
            ) from error