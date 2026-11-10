from dataclasses import dataclass

import cadquery as cq

from src.assembly.assembly_component import AssemblyComponent

@dataclass
class AssemblyResult:
    model: cq.Compound
    components: list[AssemblyComponent]