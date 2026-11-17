"""Ventilation slots above heat sources."""
from src.geometry.kernel import kernel


def vent_slots(points, z: float, thickness: float, slots: int = 4, slot_width: float = 2.0,
               slot_length: float = 16.0, pitch: float = 4.0):
    """Parallel slots centred on each (x, y) point, cut through a plate at height ``z``."""
    k = kernel()
    cut = None
    for px, py in points:
        for i in range(slots):
            x = px + (i - (slots - 1) / 2) * pitch
            shape = k.box((slot_width, slot_length, thickness * 4), (x, py, z + thickness / 2))
            cut = shape if cut is None else k.fuse(cut, shape)
    return cut
