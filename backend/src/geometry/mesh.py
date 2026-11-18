"""A tiny triangle-mesh type (numpy only) used for orientation, plate packing and export."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TriMesh:
    vertices: np.ndarray  # (N, 3) float
    faces: np.ndarray     # (M, 3) int

    def __post_init__(self):
        self.vertices = np.asarray(self.vertices, dtype=float).reshape(-1, 3)
        self.faces = np.asarray(self.faces, dtype=np.int64).reshape(-1, 3)

    def copy(self) -> 'TriMesh':
        return TriMesh(self.vertices.copy(), self.faces.copy())

    def apply_transform(self, matrix: np.ndarray) -> 'TriMesh':
        """Transform in place and return self (same convention as trimesh)."""
        m = np.asarray(matrix, dtype=float)
        self.vertices = self.vertices @ m[:3, :3].T + m[:3, 3]
        if np.linalg.det(m[:3, :3]) < 0:  # mirrored: keep normals pointing outwards
            self.faces = self.faces[:, ::-1]
        return self

    @property
    def bounds(self) -> np.ndarray:
        if len(self.vertices) == 0:
            return np.zeros((2, 3))
        return np.array([self.vertices.min(axis=0), self.vertices.max(axis=0)])

    @property
    def triangles(self) -> np.ndarray:
        return self.vertices[self.faces]

    @property
    def _cross(self) -> np.ndarray:
        t = self.triangles
        return np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])

    @property
    def area_faces(self) -> np.ndarray:
        return np.linalg.norm(self._cross, axis=1) / 2

    @property
    def face_normals(self) -> np.ndarray:
        c = self._cross
        n = np.linalg.norm(c, axis=1, keepdims=True)
        return np.divide(c, n, out=np.zeros_like(c), where=n > 0)

    @property
    def volume(self) -> float:
        t = self.triangles
        return float(np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6)

    @staticmethod
    def concatenate(meshes: list['TriMesh']) -> 'TriMesh':
        verts, faces, offset = [], [], 0
        for m in meshes:
            verts.append(m.vertices)
            faces.append(m.faces + offset)
            offset += len(m.vertices)
        if not verts:
            return TriMesh(np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64))
        return TriMesh(np.concatenate(verts), np.concatenate(faces))
