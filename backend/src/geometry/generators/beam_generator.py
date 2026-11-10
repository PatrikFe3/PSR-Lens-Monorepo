import cadquery as cq
from src.config.paths import MODELS_DIR


def create_beam(
        length: float,
        width: float,
        height: float,
) -> cq.Workplane:
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError("Length, width and height must be positive.")

    beam = (
        cq.Workplane("XY")
        .box(length, width, height)
    )
    return beam

def generate_beam(
        length: float,
        width: float,
        height: float,
) -> None:
    beam = create_beam(
        length=length,
        width=width,
        height=height,
    )

    path = MODELS_DIR / "beam.stl"

    cq.exporters.export(
        beam,
        str(path),
        exportType="STL",
    )

    print(f"Model saved to {path.resolve()}")
