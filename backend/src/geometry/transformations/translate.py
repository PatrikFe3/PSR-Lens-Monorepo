import cadquery as cq

def translate_model(
        model: cq.Workplane,
        x: float = 0,
        y: float = 0,
        z: float = 0,
) -> cq.Workplane:
    return model.translate((x, y, z))