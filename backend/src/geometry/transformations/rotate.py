import cadquery as cq

def rotate_model(
        model: cq.Workplane,
        axis_start: tuple[float, float, float],
        axis_end: tuple[float, float, float],
        angle: float,
) -> cq.Workplane:
    return model.rotate(
        axisStartPoint=axis_start,
        axisEndPoint=axis_end,
        angleDegrees=angle,
    )