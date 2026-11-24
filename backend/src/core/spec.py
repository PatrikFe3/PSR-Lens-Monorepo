"""

"""
from typing import Literal

from pydantic import BaseModel, Field


class HardwareUse(BaseModel):
    id: str
    ref: str


class PartSpec(BaseModel):
    id: str
    template: str
    params: dict = Field(default_factory=dict)


class Connection(BaseModel):
    a: str
    b: str
    kind: Literal['fixed', 'revolute']
    interface: str | None = None
    range_deg: tuple[float, float] | None = None
    rest_deg: float = 0.0

    @property
    def parent(self) -> str:
        return self.a.split('.', 1)[0]

    @property
    def parent_site(self) -> str:
        return self.a.split('.', 1)[-1]

    @property
    def child(self) -> str:
        return self.b.split('.', 1)[0]

    @property
    def child_site(self) -> str:
        return self.b.split('.', 1)[-1]


class DesignSpec(BaseModel):
    intent: str
    hardware: list[HardwareUse] = Field(default_factory=list)
    parts: list[PartSpec]
    connections: list[Connection] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)