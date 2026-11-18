"""Building blocks shared by all part templates.

A *template* turns a few parameters (most of them ``"auto"``) into solid
bodies plus named *sites*. A site is a coordinate frame on a face of the
part: its origin lies on the face and its +Z points out of the part. Two
parts are joined by mating a site of one with a site of the other.
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

# Every interface in the catalog; templates narrow this per site when needed.
ALL_INTERFACES = ('revolute_pin', 'screw_m2_5', 'dovetail', 'stud_grid')


@dataclass(frozen=True)
class Site:
    name: str
    frame: Frame
    accepts: tuple[str, ...]
    body: str = 'main'


@dataclass
class Body:
    shape: Any                     # kernel shape (cadquery Shape or preview CSG node)
    print_down: str | None = None  # face that goes on the bed: '-Z', '+Z', '+X', ...


@dataclass
class BuiltPart:
    id: str
    template: str
    params: BaseModel
    bodies: dict[str, Body]
    sites: dict[str, Site]
    # (hardware use id, 4x4 pose of the hardware's board frame in part coordinates)
    holds: list[tuple[str, np.ndarray]] = field(default_factory=list)
    # warnings found while building (e.g. a joint feature forced a new print orientation)
    notes: list = field(default_factory=list)


@dataclass
class BuildContext:
    catalog: Any
    printer: Any
    material: Any
    hardware: dict[str, Any]  # hardware use id -> HardwareSpec

    def clearance(self, fit: str) -> float:
        """Radial clearance for a fit class, scaled for the material."""
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
    sites: ClassVar[dict[str, tuple[str, ...]]]           # site name -> accepted interface ids
    hardware_categories: ClassVar[tuple[str, ...]] = ()   # categories the 'hardware' param accepts
    needs_assembly: ClassVar[bool] = False                # True: sizes depend on the solved assembly

    @property
    def site_names(self) -> list[str]:
        return list(self.sites)

    def parse(self, params: dict) -> TemplateParams:
        return self.Params.model_validate(params or {})

    def resolve(self, params: TemplateParams, ctx: BuildContext, assembly=None) -> TemplateParams:
        """Replace every ``"auto"`` by a concrete value. Default: nothing to resolve."""
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