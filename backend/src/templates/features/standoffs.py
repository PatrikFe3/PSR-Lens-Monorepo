"""
    Screw standoffs for mounting circuit boards.
"""
import numpy as np

from src.core.frames import translate
from src.geometry.kernel import kernel


def standoff_radius(pilot_diameter: float) -> float:
    return max(2.5, pilot_diameter / 2 + 1.6)


"""
    Standoff posts and their pilot holes.
    Returns (add, cut): shapes to fuse and to subtract (cut may be None).
"""
def standoffs(holes, height: float, pilot_diameter: float, pose: np.ndarray, embed: float = 0.5):

    k = kernel()
    add = cut = None
    r = standoff_radius(pilot_diameter)
    for x, y in holes:
        post = k.transform(k.cylinder(r, height + embed), pose @ translate(x, y, -height - embed))
        hole = k.transform(k.cylinder(pilot_diameter / 2, height + embed + 0.2),
                           pose @ translate(x, y, -height - embed + 0.1))
        add = post if add is None else k.fuse(add, post)
        cut = hole if cut is None else k.fuse(cut, hole)
    return add, cut