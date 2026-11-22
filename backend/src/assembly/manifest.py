"""The JSON manifest the web viewer uses to show and animate an assembly."""
import numpy as np

from src.assembly.solver import child_offset, parent_frame


def _rows(m: np.ndarray) -> list[float]:
    return [round(float(v), 6) for v in np.asarray(m).reshape(-1)]


def build_manifest(assembly, design_id, issues, hardware=None) -> dict:
    hardware = hardware or {}
    parts = []
    for pid, part in assembly.parts.items():
        j = assembly.joints.get(pid)
        entry = {
            'id': pid,
            'template': part.template,
            'parent': j.parent if j else None,
            'world': _rows(assembly.world[pid]),
            'bodies': [
                {'name': b, 'mesh': f'/designs/{design_id}/meshes/{pid}.{b}.glb'}
                for b in part.bodies
            ],
            'holds': [
                {'hardware': hid,
                 'ref': getattr(hardware.get(hid), 'id', None),
                 'pose': _rows(pose)}
                for hid, pose in part.holds
            ],
        }
        if j:
            entry['joint'] = {
                'kind': j.kind,
                'interface': j.interface.id if j.interface else None,
                'min': j.range_deg[0],
                'max': j.range_deg[1],
                'value': j.rest_deg,
                # child_world = parent_world @ parent_frame @ Rz(value) @ child_offset
                'parent_frame': _rows(parent_frame(j, assembly.parts[j.parent])),
                'child_offset': _rows(child_offset(j, part)),
            }
        parts.append(entry)

    return {
        'id': design_id,
        'units': 'mm',
        'up': 'Z',
        'matrix_order': 'row-major',
        'root': assembly.root,
        'parts': parts,
        'issues': [i.to_dict() for i in issues],
    }


def body_to_glb(shape, path, tolerance=0.1, angular=0.2):
    from src.geometry.kernel import kernel
    from src.geometry.mesh import TriMesh
    from src.manufacturing.export import write_glb

    mesh = TriMesh(*kernel().tessellate(shape, tolerance, angular))
    write_glb(mesh, path)
    return mesh
