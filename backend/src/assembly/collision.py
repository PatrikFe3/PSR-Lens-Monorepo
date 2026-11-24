"""
Collision sweep: move every revolute joint through its range and look for overlaps.
"""
from itertools import combinations, product

import numpy as np

from src.assembly.solver import solve
from src.core.issues import Issue
from src.geometry.kernel import kernel

TOLERANCE_MM3 = 1.0


def sample_poses(joints, samples: int = 5, max_combined: int = 4) -> list[dict[str, float]]:
    revolute = {c: j for c, j in joints.items() if j.kind == 'revolute'}
    if not revolute:
        return [{}]
    poses = []
    for child, j in revolute.items():
        for a in np.linspace(j.range_deg[0], j.range_deg[1], samples):
            poses.append({child: float(a)})
    if len(revolute) <= max_combined:
        ends = [(j.range_deg[0], j.rest_deg, j.range_deg[1]) for j in revolute.values()]
        poses += [dict(zip(revolute, combo)) for combo in product(*ends)]
    unique, seen = [], set()
    for p in poses:
        key = tuple(sorted((k, round(v, 6)) for k, v in p.items()))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def envelope_shape(hw, pose: np.ndarray):
    k = kernel()
    b, e = hw.board, hw.envelope
    height = e.below + b.thickness + e.above
    box = k.box((b.length, b.width, height), (b.length / 2, b.width / 2, -e.below + height / 2))
    return k.transform(box, pose)


def _overlap(a, b) -> bool:
    (alo, ahi), (blo, bhi) = a, b
    return bool(np.all(np.minimum(ahi, bhi) - np.maximum(alo, blo) > 0))


def _pose_text(pose: dict[str, float]) -> str:
    return ', '.join(f'{c}={a:g} deg' for c, a in pose.items()) or 'rest pose'


def sweep_collisions(built, joints, hardware, samples: int = 5) -> list[Issue]:
    k = kernel()
    issues, reported = [], set()
    for pose in sample_poses(joints, samples):
        assembly = solve(built, joints, pose)
        solids = []  # (owner part, label, shape, bounds, is_hardware)
        for pid, part in built.items():
            for name in part.bodies:
                s = assembly.world_shape(pid, name)
                solids.append((pid, f'{pid}.{name}', s, k.bounds(s), False))
            for hid, hold_pose in part.holds:
                s = envelope_shape(hardware[hid], assembly.world[pid] @ hold_pose)
                solids.append((pid, hid, s, k.bounds(s), True))

        for a, b in combinations(solids, 2):
            if a[0] == b[0] or (a[4] and b[4]):
                continue  # same part (designed together) or two pieces of hardware
            key = tuple(sorted((a[1], b[1])))
            if key in reported or not _overlap(a[3], b[3]):
                continue
            volume = k.intersect_volume(a[2], b[2])
            if volume <= TOLERANCE_MM3:
                continue
            reported.add(key)
            hardware_hit = a[4] or b[4]
            issues.append(Issue(
                'hardware_collision' if hardware_hit else 'collision', 'error',
                f'{key[0]} and {key[1]} overlap by {volume:.0f} mm3 at {_pose_text(pose)}.',
                part=b[0], data={'with': a[0], 'pose': pose, 'volume_mm3': round(volume, 1)},
                hint=('Limit the joint range, make the link longer, or attach the part to another site.')))
    return issues
