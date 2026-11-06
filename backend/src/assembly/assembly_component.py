from dataclasses import dataclass

@dataclass
class AssemblyComponent:
    component_type: str

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    rotation: float = 0.0