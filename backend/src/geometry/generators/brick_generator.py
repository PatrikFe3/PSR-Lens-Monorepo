import cadquery as cq

from src.geometry.primitives import create_cylinder
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
        wall_thickness: float = 1.5,
        underside_radius: float = 2.5,
        underside_depth: float = 4.0,
) -> cq.Workplane:

    if studs_x < 1 or studs_y < 1:
        raise ValueError("Stud counts must be at least 1.")

    if stud_spacing <= 0 or base_height <= 0 or stud_height <= 0:
        raise ValueError("Dimensions must be positive.")

    if stud_inner_radius >= stud_radius:
        raise ValueError("Inner radius must be smaller than outer radius.")

    if wall_thickness <= 0:
        raise ValueError("Wall thickness must be positive.")

    if underside_radius <= stud_radius:
        raise ValueError("Underside radius must be greater than stud radius.")

    if underside_depth <= 0 or underside_depth >= base_height:
        raise ValueError("Underside depth must be greater than zero and smaller than base height.")

    length = studs_x * stud_spacing
    width = studs_y * stud_spacing

    if wall_thickness * 2 >= min(length, width):
        raise ValueError("Wall thickness must be smaller than length.")

    base = create_box(
        length=length,
        width=width,
        height=base_height,
    )

    builder = ModelBuilder()
    builder.add(base)

    inner_length = length - 2 * wall_thickness
    inner_width = width - 2 * wall_thickness

    inner_height = base_height - wall_thickness

    inner_space = create_box(
        length=inner_length,
        width=inner_width,
        height=inner_height,
    )

    inner_space = translate_model(
        model=inner_space,
        z=-wall_thickness / 2,
    )

    builder.subtract(inner_space)

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

            underside_hole = create_cylinder(
                radius=underside_radius,
                height=underside_depth,
            )

            underside_hole = translate_model(
                model=underside_hole,
                x=x_position,
                y=y_position,
                z=-base_height / 2,
            )

            builder.subtract(underside_hole)

    return builder.build()

model = generate_brick(
    studs_x=4,
    studs_y=2,
)


