import cadquery as cq

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
