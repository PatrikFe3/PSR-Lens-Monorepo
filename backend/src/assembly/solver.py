"""Joints and forward kinematics: where every part sits for given joint angles.

Mating rule: the child's site frame is placed on the parent's site frame, moved
out by the interface gap, turned by the joint angle about the site Z axis, and
flipped so the two faces point at each other::

    child_world = parent_world @ Fp @ T(z=gap) @ Rz(angle) @ FLIP @ inverse(Fc)
"""
from dataclasses import dataclass, field

import numpy as np

from src.core.frames import FLIP, rot_z, translate
from src.core.issues import DesignError, Issue
from src.geometry.kernel import kernel


@dataclass(frozen=True)
class Joint:
    child: str
    parent: str
    parent_site: str
    child_site: str
    kind: str                      # 'fixed' | 'revolute'
    interface: object | None       # InterfaceSpec
    range_deg: tuple[float, float]
    rest_deg: float = 0.0

    @property
    def gap(self) -> float:
        return self.interface.gap if self.interface is not None else 0.0


def build_joints(spec, built, catalog) -> dict[str, Joint]:
    joints = {}
    for c in spec.connections:
        interface = catalog.interfaces.get(c.interface) if c.interface else None
        if c.kind == 'revolute':
            lo, hi = c.range_deg if c.range_deg else (-90.0, 90.0)
        else:
            lo = hi = c.rest_deg
        joints[c.child] = Joint(c.child, c.parent, c.parent_site, c.child_site, c.kind,
                                interface, (float(lo), float(hi)), float(c.rest_deg))
    return joints


def parent_frame(joint: Joint, parent_part) -> np.ndarray:
    return parent_part.sites[joint.parent_site].frame.matrix() @ translate(z=joint.gap)


def child_offset(joint: Joint, child_part) -> np.ndarray:
    return FLIP @ np.linalg.inv(child_part.sites[joint.child_site].frame.matrix())


@dataclass
class Assembly:
    parts: dict                     # part id -> BuiltPart
    joints: dict[str, Joint]
    root: str
    world: dict[str, np.ndarray]
    angles: dict[str, float] = field(default_factory=dict)

    def world_shape(self, pid: str, body: str):
        return kernel().transform(self.parts[pid].bodies[body].shape, self.world[pid])

    def site_world(self, pid: str, site: str) -> np.ndarray:
        return self.world[pid] @ self.parts[pid].sites[site].frame.matrix()


def _order(built, joints) -> tuple[str, list[str]]:
    roots = [pid for pid in built if pid not in joints]
    if len(roots) != 1:
        raise DesignError([Issue('no_base', 'error',
                                 f'Expected exactly one base part, found {len(roots)}: {roots}.')])
    order, frontier = [], [roots[0]]
    while frontier:
        pid = frontier.pop(0)
        order.append(pid)
        frontier += [c for c, j in joints.items() if j.parent == pid]
    if len(order) != len(built):
        missing = sorted(set(built) - set(order))
        raise DesignError([Issue('disconnected_part', 'error', f'Parts not connected to the base: {missing}.')])
    return roots[0], order


def solve(built: dict, joints: dict[str, Joint], angles: dict[str, float] | None = None) -> Assembly:
    root, order = _order(built, joints)
    angles = dict(angles or {})
    world = {root: np.eye(4)}
    used = {}
    for pid in order[1:]:
        j = joints[pid]
        angle = angles.get(pid, j.rest_deg) if j.kind == 'revolute' else j.rest_deg
        lo, hi = j.range_deg
        if j.kind == 'revolute' and not lo - 1e-9 <= angle <= hi + 1e-9:
            raise ValueError(f'Angle {angle} for joint {pid!r} is outside its range {j.range_deg}.')
        used[pid] = angle
        world[pid] = (world[j.parent] @ parent_frame(j, built[j.parent]) @ rot_z(angle)
                      @ child_offset(j, built[pid]))
    return Assembly(built, joints, root, world, used)
