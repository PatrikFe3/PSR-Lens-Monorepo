import cadquery as cq

"""
Will combine two models together
"""
def union_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:

    return model_a.union(model_b, clean=True)

"""
Will cut targeted model, and modify the surface
"""
def cut_model(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:

    return model_a.cut(model_b, clean=True)

"""
Will keep only overlapping geometry of both models
"""
def intersect_models(
        model_a: cq.Workplane,
        model_b: cq.Workplane,
) -> cq.Workplane:

    return model_a.intersect(model_b, clean=True)
