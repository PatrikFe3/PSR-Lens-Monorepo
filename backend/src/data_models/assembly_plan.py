from dataclasses import dataclass
from typing import Literal

AttachmentType = Literal[
    "top",
    "bottom",
    "left",
    "right",
    "front",
    "back",
]

@dataclass
class AssemblyInstruction:
    component_id: str
    component_type: str
    parent_id: str | None = None
    attachment: AttachmentType | None = None

@dataclass
class AssemblyPlan:
    name: str
    instructions: list[AssemblyInstruction]

