from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Face = Literal['+X', '-X', '+Y', '-Y', '+Z', '-Z']


class CatalogModel(BaseModel):
    # A misspelled YAML key is an error, not a silently ignored field.
    model_config = ConfigDict(extra='forbid')


class Board(CatalogModel):
    length: float = Field(gt=0)
    width: float = Field(gt=0)
    thickness: float = Field(gt=0)


class Envelope(CatalogModel):
    above: float = Field(gt=0)
    below: float = Field(gt=0)


class Mounting(CatalogModel):
    screw: str
    hole_diameter: float = Field(gt=0)
    holes: list[tuple[float, float]]
    standoff_height: float = Field(gt=0)


class Port(CatalogModel):
    id: str
    face: Face
    center: tuple[float, float]
    size: tuple[float, float]
    required: bool = False


class HwConnector(CatalogModel):
    id: str
    type: str
    position: tuple[float, float]
    cable_exit: Face
    cable_length: float | None = None


class HeatSource(CatalogModel):
    id: str
    position: tuple[float, float]
    power_w: float = Field(ge=0)


class HardwareSpec(CatalogModel):
    id: str
    name: str
    category: str
    description: str
    board: Board
    envelope: Envelope
    mass_g: float = Field(gt=0)
    mounting: Mounting | None = None
    ports: list[Port] = Field(default_factory=list)
    connectors: list[HwConnector] = Field(default_factory=list)
    heat_sources: list[HeatSource] = Field(default_factory=list)
    optics: dict | None = None

    @model_validator(mode='after')
    def holes_on_board(self):
        for x, y in (self.mounting.holes if self.mounting else []):
            if not (0 < x < self.board.length and 0 < y < self.board.width):
                raise ValueError(f'{self.id}: hole ({x}, {y}) is off the board')
        return self


class InterfaceSpec(CatalogModel):
    id: str
    kind: Literal['fixed', 'revolute']
    description: str
    fit: Literal['press', 'snug', 'sliding', 'loose']
    params: dict[str, float]
    gap: float = 0.0
    male_feature: str
    female_feature: str
    hardware: list[dict] = Field(default_factory=list)
