from dataclasses import dataclass

@dataclass
class AssemblyInstruction:
    component_id: str
    component_type: str
    parent_id: str | None = None
    attachment: str | None = None

@dataclass
class AssemblyPlan:
    name: str
    instructions: list[AssemblyInstruction]