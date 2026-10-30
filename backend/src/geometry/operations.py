import cadquery as cq

def create_cylinder(
        radius: float,
        height: float,
) -> cq.Workplane:

    if radius <= 0 or height <= 0:
        raise ValueError("radius and height must be positive.")

    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
    )

def add_circular_ribs(
        model: cq.Workplane,
        radius: float,
        height: float,
        count: int,
        rib_width: float= 4.0,
        rib_thickness: float= 3.0,
        overlap: float = 1.0,
) -> cq.Workplane:

    if count < 1:
        raise ValueError("Count must be at least 1.")

    if radius <= 0 or height <= 0:
        raise ValueError("Radius and height must be positive.")

    if rib_width <= 0 or rib_thickness <= 0:
        raise ValueError("Rib dimensions must be positive.")

    if overlap <= 0 or overlap >= min(radius, rib_thickness):
        raise ValueError("Overlap must be between 0 and 1.")

    for index in range(count):
        #counting angle
        angle = index * 360 / count

        rib = (
            cq.Workplane("XY").box(
                rib_thickness,
                rib_width,
                height,
                centered=(True, True, False),
            ).translate(
                (
                    radius + rib_thickness / 2 - overlap,
                    0,
                    0,
                )
            ).rotate(
                (0,0,0),
                (0,0,1),
                angle,
            )
        )

        model = model.union(rib)

    return model


def smooth_bevel(
        model: cq.Workplane,
        radius: float,
) -> cq.Workplane:
    if radius <= 0:
        raise ValueError("Radius must be at least 0.1")
    try:
        return model.edges().fillet(radius)
    except Exception as error:
        raise ValueError(f"Fillet with radius {radius} mm failed."
                         "The radius may be too large for the selected edges, "
                         "or the model geometry may not support this operation."
                         ) from error


def hard_bevel(
        model: cq.Workplane,
        distance: float,
) -> cq.Workplane:
    if distance <= 0:
        raise ValueError("Distance must be at least 0.1")
    try:
        return model.edges().chamfer(distance)
    except Exception as error:
        raise ValueError(f"Chamfer with distance {distance} mm failed."
                         "The distance may be too large for the selected edges, "
                         "or the model geometry may not support this operation."
                         ) from error

def add_twisted_ribs(
        model: cq.Workplane,
        radius: float,
        height: float,
        count: int,
        twist_angle: float= 180.0,
        rib_width: float= 4.0,
        rib_thickness: float= 3.0,
        overlap: float = 1.0,
) -> cq.Workplane:

    if count < 1:
        raise ValueError("Count must be at least 1.")

    if radius <= 0 or height <= 0:
        raise ValueError("Radius and height must be positive.")

    if rib_width <= 0 or rib_thickness <= 0:
        raise ValueError("Rib dimensions must be positive.")

    if overlap <= 0 or overlap >= min(radius, rib_thickness):
        raise ValueError("Overlap must be between 0 and 1.")


    inner_radius = radius - overlap
    outer_radius = inner_radius + rib_thickness

    for index in range(count):
        angle = index * 360 / count

        rib = (
            cq.Workplane("XY")
            .moveTo(inner_radius, -rib_width / 2)
            .lineTo(outer_radius, -rib_width / 2)
            .lineTo(outer_radius, rib_width / 2)
            .lineTo(inner_radius, rib_width / 2)
            .close()
            .twistExtrude(
                distance=height,
                angleDegrees=twist_angle,
                combine=False,
            )
            .rotate(
                (0,0,0),
                (0,0,1),
                angle,
            )

        )

        model = model.union(rib)

    return model

def union_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    return model_a.union(model_b, clean=True)

def cut_model(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    return model_a.cut(model_b, clean=True)

def intersect_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    return model_a.intersect(model_b, clean=True)

#  Discuss these cadquery topics
#  irregular_grid
#  cq terrain
