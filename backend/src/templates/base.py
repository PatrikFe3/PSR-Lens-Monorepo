"""
    Building blocks shared by all part templates.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal

import numpy as np
from pydantic import BaseModel, ConfigDict

from src.core.frames import Frame

AUTO = 'auto'
Auto = Literal['auto']

ALL_INTERFACES = ('revolute_pin', 'screw_m2_5', 'dovetail', 'stud_grid')


@dataclass(frozen=True)
class Site:
    name: str
    frame: Frame
    accepts: tuple[str, ...]
    body: str = 'main'


@dataclass
class Body:
    shape: Any
    print_down: str | None = None


@dataclass
class BuiltPart:
    id: str
    template: str
    params: BaseModel
    bodies: dict[str, Body]
    sites: dict[str, Site]
    holds: list[tuple[str, np.ndarray]] = field(default_factory=list)
    notes: list = field(default_factory=list)


@dataclass
class BuildContext:
    catalog: Any
    printer: Any
    material: Any
    hardware: dict[str, Any]  # hardware use id -> HardwareSpec

    def clearance(self, fit: str) -> float:
        return self.printer.fit_classes[fit] * self.material.clearance_factor

    def pilot_diameter(self, screw: str, fallback: float) -> float:
        return self.material.pilot_hole.get(screw, fallback)


class TemplateParams(BaseModel):
    model_config = ConfigDict(extra='forbid')


def auto(value, default):
    return default if value == AUTO or value is None else value


class Template(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    Params: ClassVar[type[TemplateParams]]
    sites: ClassVar[dict[str, tuple[str, ...]]]
    hardware_categories: ClassVar[tuple[str, ...]] = ()
    needs_assembly: ClassVar[bool] = False

    @property
    def site_names(self) -> list[str]:
        return list(self.sites)

    def parse(self, params: dict) -> TemplateParams:
        return self.Params.model_validate(params or {})


    def resolve(self, params: TemplateParams, ctx: BuildContext, assembly=None) -> TemplateParams:
        return params

    @abstractmethod
    def build(self, part_id: str, params: TemplateParams, ctx: BuildContext) -> BuiltPart:
        ...

    def describe(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'sites': {k: list(v) for k, v in self.sites.items()},
            'hardware_categories': list(self.hardware_categories),
            'params': self.Params.model_json_schema(),
        }