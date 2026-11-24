"""
Hollow boxes and plates.
"""
from src.geometry.kernel import kernel

"""

"""
def open_tray(length: float, width: float, height: float, wall: float, floor: float):

    k = kernel()
    outer = k.box((length, width, height), (0, 0, height / 2))
    inner_h = height - floor + 1.0  # runs past the top so the top is open
    inner = k.box((length - 2 * wall, width - 2 * wall, inner_h), (0, 0, floor + inner_h / 2))
    return k.cut(outer, inner)

"""

"""
def lid(length: float, width: float, thickness: float, z: float,
        lip_length: float, lip_width: float, lip_height: float):

    k = kernel()
    plate = k.box((length, width, thickness), (0, 0, z + thickness / 2))
    lip_outer = k.box((lip_length, lip_width, lip_height + 0.5), (0, 0, z - lip_height / 2 + 0.25))
    lip_inner = k.box((lip_length - 3.2, lip_width - 3.2, lip_height + 1.0), (0, 0, z - lip_height / 2))
    return k.fuse(plate, k.cut(lip_outer, lip_inner))