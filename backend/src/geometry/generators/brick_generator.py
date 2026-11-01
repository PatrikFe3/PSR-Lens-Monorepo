import cadquery as cq

from src.geometry.primitives import create_pipe
from src.geometry.primitives import (
    create_box,
)

from src.geometry.transformations.translate import (
    translate_model,
)

from src.geometry.model_builder import ModelBuilder

def generate_brick(
        studs_x: int = 2,
        studs_y: int = 1,
        stud_spacing: float = 8.0,
        base_height: float = 5.0,
        stud_radius: float = 2.4,
        stud_inner_radius: float = 1.5,
        stud_height: float = 1.8,
) -> cq.Workplane:

    if studs_x < 1 or studs_y < 1:
        raise ValueError("Stud counts must be at least 1.")

    if stud_spacing <= 0 or base_height <= 0 or stud_height <= 0:
        raise ValueError("Dimensions must be positive.")

    if stud_inner_radius >= stud_radius:
        raise ValueError("Inner radius must be smaller than outer radius.")

    length = studs_x * stud_spacing
    width = studs_y * stud_spacing

    base = create_box(
        length=length,
        width=width,
        height=base_height,
    )

    builder = ModelBuilder()
    builder.add(base)

    print(f"Base dimensions: {length} x {width}")

    for x_index in range(studs_x):

        for y_index in range(studs_y):

            x_position = (x_index - (studs_x - 1) / 2) * stud_spacing
            y_position = (y_index - (studs_y - 1) / 2) * stud_spacing

            print(f"Stud position: x={x_position} y={y_position}")

            stud = create_pipe(
                outer_radius=stud_radius,
                inner_radius=stud_inner_radius,
                length=stud_height,
            )

            stud = translate_model(
                model=stud,
                x=x_position,
                y=y_position,
                z=base_height / 2,
            )

            builder.add(stud)

    return builder.build()

