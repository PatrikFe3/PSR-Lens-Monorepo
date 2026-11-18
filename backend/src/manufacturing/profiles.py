from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Rect = tuple[float, float, float, float]


class _Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Bed(_Strict):
    shape: Literal['rect', 'circle'] = 'rect'
    width: float = Field(gt=0)
    depth: float = Field(gt=0)
    margin: float = Field(default=5.0, ge=0)
    # Areas the nozzle cannot use, as (x0, y0, x1, y1). Each must span a full bed edge.
    exclusions: list[Rect] = Field(default_factory=list)


class PrinterSpec(_Strict):
    id: str
    name: str
    technology: Literal['FDM', 'SLA'] = 'FDM'
    bed: Bed
    max_height: float = Field(gt=0)
    nozzle_diameter: float = Field(default=0.4, gt=0)
    min_wall_lines: int = Field(default=2, gt=0)
    default_wall: float = 2.0
    min_gap: float = 1.0
    part_spacing: float = Field(default=6.0, gt=0)
    fit_classes: dict[str, float]

    @property
    def min_wall(self) -> float:
        return self.nozzle_diameter * self.min_wall_lines

    @model_validator(mode='after')
    def required_fits(self):
        missing = {'press', 'snug', 'sliding', 'loose'} - set(self.fit_classes)
        if missing:
            raise ValueError(f'{self.id}: missing fit classes {sorted(missing)}')
        return self


class MaterialSpec(_Strict):
    id: str
    name: str
    density_g_cm3: float = Field(gt=0)
    clearance_factor: float = Field(default=1.0, gt=0)
    brim: float = Field(default=1.0, ge=0)
    pilot_hole: dict[str, float]
    insert_hole: dict[str, tuple[float, float]] = Field(default_factory=dict)
