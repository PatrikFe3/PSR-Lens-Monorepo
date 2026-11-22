"""
Turn printable bodies into one or more build plates.
"""
from pathlib import Path

import numpy as np

from src.core.frames import rot_z, translate
from src.core.issues import DesignError, Issue
from src.geometry.mesh import TriMesh
from src.manufacturing.export import write_stl
from src.manufacturing.orientation import orient
from src.manufacturing.packing import Item, PartTooLarge, layout, usable_rect


def plan_plates(
        meshes: dict[str, TriMesh],
        hints: dict[str, str | None],
        printer,
        material,
        mode='spread'
) -> dict:
    lay_flat, sizes, items, issues = {}, {}, [], []
    brim = material.brim
    for key, mesh in meshes.items():
        m = orient(mesh, hints.get(key))
        lo, hi = mesh.copy().apply_transform(m).bounds
        size = hi - lo
        if size[2] > printer.max_height:
            issues.append(Issue(
                'part_too_tall', 'error',
                f'{key} is {size[2]:.0f} mm tall; {printer.name} prints up to {printer.max_height:.0f} mm.',
                part=key.split('.')[0], hint='Split the part or shorten it.'))
        lay_flat[key], sizes[key] = m, size
        items.append(Item(key, size[0] + 2 * brim, size[1] + 2 * brim))

    placements = []
    try:
        placements = layout(items, printer, mode)
    except PartTooLarge as error:
        issues.append(Issue(
            'part_too_large', 'error', f'{error} does not fit the bed of {printer.name}.',
            part=str(error).split('.')[0], hint='Split the part with a dowel joint.'))
    if issues:
        raise DesignError(issues)

    plates: dict[int, list] = {}
    for p in placements:
        # rot_z(90) moves the footprint to x in [-depth, 0]; shift it back by the body depth.
        turn = translate(sizes[p.key][1], 0, 0) @ rot_z(90) if p.rotated else np.eye(4)
        matrix = translate(p.x + brim, p.y + brim, 0) @ turn @ lay_flat[p.key]
        plates.setdefault(p.plate, []).append({'key': p.key, 'matrix': matrix})
    return {
        'printer': printer.id,
        'bed': printer.bed.model_dump(),
        'usable': usable_rect(printer.bed),
        'max_height': printer.max_height,
        'plates': [plates[i] for i in sorted(plates)],
    }


def export_plate(meshes: dict[str, TriMesh], plate_items, path) -> Path:
    placed = [meshes[i['key']].copy().apply_transform(i['matrix']) for i in plate_items]
    return write_stl(TriMesh.concatenate(placed), path)