from dataclasses import dataclass
import numpy as np

Vec3 = tuple[float, float, float]

def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)

    if n < 1e-9:
        raise ValueError('Zero-length direction.')
    return v / n

@dataclass(frozen=True)
class Frame:
    origin: Vec3 = (0.0, 0.0, 0.0)
    z: Vec3 = (0.0, 0.0, 1.0)
    x: Vec3 = (1.0, 0.0, 0.0)

    def matrix(self) -> np.ndarray:
        z = _unit(self.z)
        x = np.asarray(self.x, dtype=float)
        x = _unit(x - np.dot(x, z) * z)
        y = np.cross(z, x)
        m = np.eye(4)
        m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, self.origin
        return m

FLIP = np.diag([1.0, -1.0, -1.0, 1.0])

def rot_x(deg: float) -> np.ndarray:
    a = np.radians(deg)
    m = np.eye(4)
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = np.cos(a), -np.sin(a), np.sin(a), np.cos(a)
    return m


def rot_y(deg: float) -> np.ndarray:
    a = np.radians(deg)
    m = np.eye(4)
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = np.cos(a), np.sin(a), -np.sin(a), np.cos(a)
    return m


def rot_z(deg: float) -> np.ndarray:
    a = np.radians(deg)
    m = np.eye(4)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = np.cos(a), -np.sin(a), np.sin(a), np.cos(a)
    return m


def translate(x=0.0, y=0.0, z=0.0) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def apply(matrix: np.ndarray, points) -> np.ndarray:
    pts = np.asarray(points, dtype=float).reshape(-1, 3)
    return pts @ matrix[:3, :3].T + matrix[:3, 3]
