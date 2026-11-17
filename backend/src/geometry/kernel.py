"""Geometry kernel used by the new design pipeline.

Every solid-modelling call of the new system goes through this module, so
the rest of the code never imports cadquery directly.

Two backends exist:

* ``cadquery`` - exact B-rep solids (OpenCascade). Use this for real prints.
* ``preview``  - pure numpy constructive-solid-geometry, sampled on a grid.
  Volumes, collisions and meshes are approximate (meshes look blocky), but it
  runs anywhere numpy runs. Used automatically when cadquery is missing, and
  handy for fast tests.

Select with the ``PSR_KERNEL`` environment variable (``auto`` | ``cadquery`` |
``preview``) or :func:`set_kernel`.
"""
from __future__ import annotations

import os
import warnings
from dataclasses import dataclass

import numpy as np

Mesh = tuple[np.ndarray, np.ndarray]  # (vertices (N, 3) float, faces (M, 3) int)


# --------------------------------------------------------------------------- cadquery
class CadQueryKernel:
    name = 'cadquery'
    exact = True

    def __init__(self):
        import cadquery as cq  # noqa: F401  (raises ImportError when missing)
        self.cq = cq

    def box(self, size, center=(0.0, 0.0, 0.0)):
        dx, dy, dz = map(float, size)
        cx, cy, cz = map(float, center)
        return self.cq.Solid.makeBox(dx, dy, dz, pnt=self.cq.Vector(cx - dx / 2, cy - dy / 2, cz - dz / 2))

    def cylinder(self, radius, height, base=(0.0, 0.0, 0.0)):
        return self.cq.Solid.makeCylinder(float(radius), float(height),
                                          pnt=self.cq.Vector(*map(float, base)),
                                          dir=self.cq.Vector(0, 0, 1))

    def prism(self, points, height, z0=0.0):
        wp = (self.cq.Workplane('XY', origin=(0, 0, float(z0)))
              .polyline([tuple(map(float, p)) for p in points]).close()
              .extrude(float(height)))
        return wp.val()

    def transform(self, shape, matrix):
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
        from OCP.gp import gp_Trsf

        m = np.asarray(matrix, dtype=float)
        # Remove rounding noise (e.g. cos(90 deg) = 6e-17) so OpenCascade accepts it as a pure rotation.
        u, _, vt = np.linalg.svd(m[:3, :3])
        r = u @ vt
        r[np.abs(r) < 1e-12] = 0.0
        trsf = gp_Trsf()
        trsf.SetValues(r[0, 0], r[0, 1], r[0, 2], m[0, 3],
                       r[1, 0], r[1, 1], r[1, 2], m[1, 3],
                       r[2, 0], r[2, 1], r[2, 2], m[2, 3])
        return self.cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, trsf, True).Shape())

    def fuse(self, a, b):
        return a.fuse(b).clean()

    def cut(self, a, b):
        return a.cut(b).clean()

    def volume(self, shape) -> float:
        return float(shape.Volume())

    def center(self, shape) -> np.ndarray:
        c = self.cq.Shape.centerOfMass(shape)
        return np.array([c.x, c.y, c.z])

    def bounds(self, shape) -> tuple[np.ndarray, np.ndarray]:
        bb = shape.BoundingBox()
        return np.array([bb.xmin, bb.ymin, bb.zmin]), np.array([bb.xmax, bb.ymax, bb.zmax])

    def intersect_volume(self, a, b) -> float:
        try:
            return float(a.intersect(b).Volume())
        except Exception:  # OCC can fail on degenerate (touching) inputs
            return 0.0

    def tessellate(self, shape, tolerance=0.1, angular=0.2) -> Mesh:
        vertices, triangles = shape.tessellate(tolerance, angular)
        v = np.array([(p.x, p.y, p.z) for p in vertices], dtype=float).reshape(-1, 3)
        f = np.array(triangles, dtype=np.int64).reshape(-1, 3)
        return v, f


# --------------------------------------------------------------------------- preview
_EPS = 1e-6


@dataclass(frozen=True)
class _Prim:
    kind: str            # 'box' | 'cyl' | 'prism'
    params: tuple
    matrix: tuple        # world-from-local 4x4, flattened (hashable)

    @property
    def m(self) -> np.ndarray:
        return np.array(self.matrix).reshape(4, 4)

    def local_corners(self) -> np.ndarray:
        if self.kind == 'box':
            dx, dy, dz = self.params
            xs, ys, zs = (-dx / 2, dx / 2), (-dy / 2, dy / 2), (-dz / 2, dz / 2)
        elif self.kind == 'cyl':
            r, h = self.params
            xs, ys, zs = (-r, r), (-r, r), (0.0, h)
        else:
            pts, h = self.params
            arr = np.array(pts)
            xs, ys, zs = (arr[:, 0].min(), arr[:, 0].max()), (arr[:, 1].min(), arr[:, 1].max()), (0.0, h)
        return np.array([(x, y, z) for x in xs for y in ys for z in zs])

    def contains(self, pts: np.ndarray) -> np.ndarray:
        m = self.m
        local = (pts - m[:3, 3]) @ m[:3, :3]  # inverse of a rigid transform
        x, y, z = local[:, 0], local[:, 1], local[:, 2]
        if self.kind == 'box':
            dx, dy, dz = self.params
            return ((np.abs(x) < dx / 2 - _EPS) & (np.abs(y) < dy / 2 - _EPS)
                    & (np.abs(z) < dz / 2 - _EPS))
        if self.kind == 'cyl':
            r, h = self.params
            return (x * x + y * y < (r - _EPS) ** 2) & (z > _EPS) & (z < h - _EPS)
        pts2d, h = self.params
        inside = (z > _EPS) & (z < h - _EPS)
        poly = np.array(pts2d)
        for (x0, y0), (x1, y1) in zip(poly, np.roll(poly, -1, axis=0)):
            inside &= (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0) > _EPS  # counter-clockwise
        return inside


@dataclass(frozen=True)
class _Node:
    op: str              # 'prim' | 'union' | 'diff'
    prim: _Prim | None = None
    children: tuple = ()


class PreviewKernel:
    """Approximate CSG kernel: exact point-membership, grid-sampled measurements."""
    name = 'preview'
    exact = False

    def __init__(self, resolution: float | None = None):
        self.res = float(resolution or os.getenv('PSR_PREVIEW_RES', '1.0'))

    # construction
    @staticmethod
    def _prim(kind, params, matrix=None):
        m = np.eye(4) if matrix is None else np.asarray(matrix, dtype=float)
        return _Node('prim', _Prim(kind, params, tuple(m.reshape(-1))))

    def box(self, size, center=(0.0, 0.0, 0.0)):
        m = np.eye(4)
        m[:3, 3] = center
        return self._prim('box', tuple(map(float, size)), m)

    def cylinder(self, radius, height, base=(0.0, 0.0, 0.0)):
        m = np.eye(4)
        m[:3, 3] = base
        return self._prim('cyl', (float(radius), float(height)), m)

    def prism(self, points, height, z0=0.0):
        pts = [tuple(map(float, p)) for p in points]
        area2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
        if area2 < 0:
            pts = pts[::-1]
        m = np.eye(4)
        m[2, 3] = z0
        return self._prim('prism', (tuple(pts), float(height)), m)

    def transform(self, shape: _Node, matrix):
        matrix = np.asarray(matrix, dtype=float)
        if shape.op == 'prim':
            p = shape.prim
            return _Node('prim', _Prim(p.kind, p.params, tuple((matrix @ p.m).reshape(-1))))
        return _Node(shape.op, None, tuple(self.transform(c, matrix) for c in shape.children))

    def fuse(self, a, b):
        return _Node('union', None, (a, b))

    def cut(self, a, b):
        return _Node('diff', None, (a, b))

    # queries
    def _contains(self, shape: _Node, pts: np.ndarray) -> np.ndarray:
        if shape.op == 'prim':
            return shape.prim.contains(pts)
        if shape.op == 'union':
            out = np.zeros(len(pts), dtype=bool)
            for c in shape.children:
                out |= self._contains(c, pts)
            return out
        keep = self._contains(shape.children[0], pts)
        if keep.any():
            idx = np.nonzero(keep)[0]
            keep[idx[self._contains(shape.children[1], pts[idx])]] = False
        return keep

    def bounds(self, shape: _Node) -> tuple[np.ndarray, np.ndarray]:
        if shape.op == 'prim':
            p = shape.prim
            corners = p.local_corners() @ p.m[:3, :3].T + p.m[:3, 3]
            return corners.min(axis=0), corners.max(axis=0)
        if shape.op == 'diff':
            return self.bounds(shape.children[0])
        bs = [self.bounds(c) for c in shape.children]
        return np.min([b[0] for b in bs], axis=0), np.max([b[1] for b in bs], axis=0)

    def _step(self, lo, hi) -> float:
        """Grid step: the configured resolution, finer for thin shapes (>= 4 samples across)."""
        thinnest = float(np.min(np.asarray(hi) - np.asarray(lo)))
        return max(min(self.res, thinnest / 4), 0.05)

    def _grid(self, lo, hi, step=None):
        step = step or self.res
        axes = [np.arange(a + step / 2, b, step) for a, b in zip(lo, hi)]
        if any(len(a) == 0 for a in axes):
            return axes, np.zeros((0, 3))
        g = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3)
        return axes, g

    def _inside_points(self, shape):
        lo, hi = self.bounds(shape)
        step = self._step(lo, hi)
        _, pts = self._grid(lo, hi, step)
        return (pts[self._contains(shape, pts)] if len(pts) else pts), step

    def volume(self, shape) -> float:
        pts, step = self._inside_points(shape)
        return float(len(pts) * step ** 3)

    def center(self, shape) -> np.ndarray:
        pts, _ = self._inside_points(shape)
        if len(pts) == 0:
            lo, hi = self.bounds(shape)
            return (lo + hi) / 2
        return pts.mean(axis=0)

    def intersect_volume(self, a, b) -> float:
        (alo, ahi), (blo, bhi) = self.bounds(a), self.bounds(b)
        lo, hi = np.maximum(alo, blo), np.minimum(ahi, bhi)
        if np.any(hi - lo <= 0):
            return 0.0
        step = self._step(lo, hi)
        _, pts = self._grid(lo, hi, step)
        if len(pts) == 0:
            return 0.0
        inside = self._contains(a, pts)
        if inside.any():
            idx = np.nonzero(inside)[0]
            inside[idx] = self._contains(b, pts[idx])
        return float(inside.sum() * step ** 3)

    def tessellate(self, shape, tolerance=0.1, angular=0.2) -> Mesh:
        """Voxel surface mesh (blocky) - fine for previews and plate planning."""
        lo, hi = self.bounds(shape)
        lo, hi = lo - self.res, hi + self.res
        axes, pts = self._grid(lo, hi)
        dims = tuple(len(a) for a in axes)
        occ = self._contains(shape, pts).reshape(dims) if len(pts) else np.zeros(dims, bool)
        origin = np.array([a[0] for a in axes]) - self.res / 2
        quads = []
        # For each axis and direction, emit the face between a filled and an empty voxel.
        for axis in range(3):
            for direction in (-1, 1):
                neighbour = np.roll(occ, -direction, axis=axis)
                edge = [slice(None)] * 3
                edge[axis] = -1 if direction == 1 else 0
                neighbour[tuple(edge)] = False
                cells = np.argwhere(occ & ~neighbour)
                if len(cells) == 0:
                    continue
                base = cells.astype(float)
                if direction == 1:
                    base[:, axis] += 1
                u, v = [a for a in range(3) if a != axis]
                corners = np.zeros((len(cells), 4, 3))
                for k, (du, dv) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
                    corners[:, k] = base
                    corners[:, k, u] += du
                    corners[:, k, v] += dv
                # keep the outward winding consistent: (u, v, axis) right-handed or not
                right_handed = (v - u) % 3 == 1
                if (direction == 1) != right_handed:
                    corners = corners[:, ::-1]
                quads.append(corners)
        if not quads:
            return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
        q = np.concatenate(quads) * self.res + origin
        verts, inverse = np.unique(np.round(q.reshape(-1, 3), 6), axis=0, return_inverse=True)
        idx = inverse.reshape(-1, 4)
        faces = np.concatenate([idx[:, [0, 1, 2]], idx[:, [0, 2, 3]]])
        return verts, faces.astype(np.int64)


# --------------------------------------------------------------------------- selection
_active = None


def set_kernel(name: str = 'auto'):
    """Choose the backend: 'auto' (cadquery if installed), 'cadquery' or 'preview'."""
    global _active
    name = (name or 'auto').lower()
    if name in ('auto', 'cadquery'):
        try:
            _active = CadQueryKernel()
            return _active
        except ImportError:
            if name == 'cadquery':
                raise
            warnings.warn('cadquery is not installed: using the approximate preview kernel. '
                          'Install it with "conda install -c conda-forge cadquery".', stacklevel=2)
    elif name != 'preview':
        raise ValueError(f'Unknown kernel {name!r}. Use auto, cadquery or preview.')
    _active = PreviewKernel()
    return _active


def kernel():
    """The active kernel (selected from PSR_KERNEL on first use)."""
    if _active is None:
        set_kernel(os.getenv('PSR_KERNEL', 'auto'))
    return _active
