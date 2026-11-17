"""Screw standoffs for mounting circuit boards."""
import numpy as np

from src.core.frames import translate
from src.geometry.kernel import kernel


def standoff_radius(pilot_diameter: float) -> float:
    return max(2.5, pilot_diameter / 2 + 1.6)


def standoffs(holes, height: float, pilot_diameter: float, pose: np.ndarray, embed: float = 0.5):
    """Standoff posts and their pilot holes.

    ``holes`` are (x, y) positions in board coordinates. ``pose`` maps the board
    frame (z = 0 is the board's underside) to part coordinates; the posts grow
    from z = -height (the mounting surface) up to the board, starting ``embed`` mm
    inside the surface so they fuse with it.

    Returns ``(add, cut)``: shapes to fuse and to subtract (``cut`` may be None).
    """
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