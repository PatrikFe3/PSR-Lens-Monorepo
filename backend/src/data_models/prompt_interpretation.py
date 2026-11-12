from dataclasses import dataclass
from src.data_models.assembly_plan import AssemblyPlan

@dataclass(frozen=True)
class PromptInterpretation:
    object_type: str
    assembly_plan: AssemblyPlan