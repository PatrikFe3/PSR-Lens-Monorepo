import cadquery as cq

def mirror_model(
        model: cq.Workplane,
        plane: str = "YZ",
) -> cq.Workplane:
    if model is None:
        raise ValueError("Model is empty or None.")

    if plane not in ["XY", "XZ", "YZ"]:
        raise ValueError("Plan must be XY, XZ, or YZ.")

    return model.mirror(plane)

def create_symmetric_model(
        model: cq.Workplane,
        plane: str = "YZ",
) -> cq.Workplane:

    mirrored_model = mirror_model(
        model=model,
        plane=plane,
    )

    return model.union(
        mirrored_model,
        clean=True,
    )

