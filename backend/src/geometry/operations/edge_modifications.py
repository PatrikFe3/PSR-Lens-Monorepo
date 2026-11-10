import cadquery as cq

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
