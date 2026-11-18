"""Openings in enclosure walls for ports and cables."""
from src.geometry.kernel import kernel


def port_cutouts(hw, board_x0: float, board_y0: float, board_top_z: float,
                 inner_length: float, inner_width: float, wall: float, margin: float = 1.0):
    """Cut shapes for every side port (+/-X, +/-Y) of a board.

    The board's corner sits at (board_x0, board_y0) in part coordinates and its top
    surface at ``board_top_z``. A port's ``center`` is (position along the face,
    height above the board top).
    """
    k = kernel()
    cut = None
    depth = wall * 3
    for port in hw.ports:
        (u, v), (w, h) = port.center, port.size
        w, h = w + 2 * margin, h + 2 * margin
        z = board_top_z + v
        if port.face in ('-Y', '+Y'):
            y = (inner_width / 2 + wall / 2) * (1 if port.face == '+Y' else -1)
            shape = k.box((w, depth, h), (board_x0 + u, y, z))
        elif port.face in ('-X', '+X'):
            x = (inner_length / 2 + wall / 2) * (1 if port.face == '+X' else -1)
            shape = k.box((depth, w, h), (x, board_y0 + u, z))
        else:  # +Z / -Z ports are handled by the lid / floor
            continue
        cut = shape if cut is None else k.fuse(cut, shape)
    return cut


def lid_slots(hw, board_x0: float, board_y0: float, lid_z: float, lid_thickness: float,
              slot=(18.0, 4.0)):
    """Slots in the lid for ribbon cables that leave the board upwards (+Z)."""
    k = kernel()
    cut = None
    for c in hw.connectors:
        if c.cable_exit != '+Z':
            continue
        x, y = board_x0 + c.position[0], board_y0 + c.position[1]
        shape = k.box((slot[0], slot[1], lid_thickness * 4), (x, y, lid_z + lid_thickness / 2))
        cut = shape if cut is None else k.fuse(cut, shape)
    return cut
