import cadquery as cq

def union_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    """Will combine two models together"""
    return model_a.union(model_b, clean=True)

def cut_model(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    """Will cut targeted model, and modify the surface"""
    return model_a.cut(model_b, clean=True)

def intersect_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:
    """Will keep only overlapping geometry of both models"""
    return model_a.intersect(model_b, clean=True)
