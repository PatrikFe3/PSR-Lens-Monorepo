import numpy as np

from src.core.frames import rot_x, rot_y, translate
from src.geometry.mesh import TriMesh

# Rotation that turns the named face of a body downwards (onto the bed).
_DOWN = {
    '-Z': np.eye(4),
    '+Z': rot_x(180),
    '+X': rot_y(90),
    '-X': rot_y(-90),
    '+Y': rot_x(-90),
    '-Y': rot_x(90),
}

def _score(mesh: TriMesh, max_overhang_deg=45.0) -> float:
    z = mesh.triangles[:, :, 2]
    nz = mesh.face_normals[:, 2]
    on_bed = (nz < -0.99) & (z.max(axis=1) < z.min() + 0.05)
    overhang = (nz < -np.sin(np.radians(max_overhang_deg))) & ~on_bed
    height = z.max() - z.min()
    return mesh.area_faces[on_bed].sum() - 0.5 * mesh.area_faces[overhang].sum() - 2.0 * height


def orient(mesh: TriMesh, hint: str | None) -> np.ndarray:
    if hint:
        if hint not in _DOWN:
            raise ValueError(f'Unknown print direction {hint!r}. Use one of {sorted(_DOWN)}.')
        rotation = _DOWN[hint]
    else:
        rotation = max(_DOWN.values(), key=lambda r: _score(mesh.copy().apply_transform(r)))
    lo = mesh.copy().apply_transform(rotation).bounds[0]
    return translate(*(-lo)) @ rotation
