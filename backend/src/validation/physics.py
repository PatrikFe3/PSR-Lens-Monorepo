from itertools import product
import numpy as np
from src.assembly.solver import solve
from src.core.issues import Issue
from src.geometry.kernel import kernel

def center_of_mass(assembly, hardware, density_g_cm3, fill=0.5):
    k = kernel()
    total, moment = 0.0, np.zeros(3)
    for pid, part in assembly.parts.items():
        for name in part.bodies:
            shape = assembly.world_shape(pid, name)
            mass = k.volume(shape) / 1000 * density_g_cm3 * fill
            total, moment = total + mass, moment + mass * k.center(shape)

        for hid, pose in part.holds:
            hw = hardware[hid]
            local = np.array([hw.board.length / 2, hw.board.width / 2, hw.board.thickness, 1.0])
            centre = (assembly.world[pid] @ pose @ local)[:3]
            total, moment = total + hw.mass_g, moment + hw.mass_g * centre
    if total <= 0:
        raise ValueError('The assembly has no mass.')
    return moment / total, total

def support_box(assembly, margin=0.15):
    k = kernel()
    lows, highs = [], []
    for name in assembly.parts[assembly.root].bodies:
        lo, hi = k.bounds(assembly.world_shape(assembly.root, name))
        lows.append(lo)
        highs.append(hi)
    lo, hi = np.min(lows, axis=0), np.max(highs, axis=0)
    dx, dy = (hi[0] - lo[0]) * margin, (hi[1] - lo[1]) * margin
    return lo[0] + dx, lo[1] + dy, hi[0] - dx, hi[1] - dy

def stability_poses(joints, max_joints: int = 4) -> list[dict[str, float]]:
    revolute = [c for c, j in joints.items() if j.kind == 'revolute']
    if not revolute:
        return [{}]
    if len(revolute) <= max_joints:
        ends = [sorted({joints[c].range_deg[0], joints[c].rest_deg, joints[c].range_deg[1]}) for c in revolute]
        return [dict(zip(revolute, combo)) for combo in product(*ends)]
    return [{c: joints[c].range_deg[i] for c in revolute} for i in (0, 1)]


def check_stability(built, joints, hardware, material) -> list[Issue]:
    issues = []
    for angles in stability_poses(joints):
        assembly = solve(built, joints, angles)
        (x, y, _), mass = center_of_mass(assembly, hardware, material.density_g_cm3)
        x0, y0, x1, y1 = support_box(assembly)
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            pose = ', '.join(f'{c}={a:g} deg' for c, a in angles.items()) or 'rest pose'
            issues.append(Issue(
                'tips_over',
                'error',
                f'Centre of mass ({x:.0f}, {y:.0f}) mm leaves the base at {pose}.',
                part=assembly.root, hint='Enlarge the base footprint or shorten the arm.',
                data={'com': [round(float(x), 1), round(float(y), 1)], 'mass_g': round(mass, 1),
                      'support': [round(float(v), 1) for v in (x0, y0, x1, y1)], 'pose': angles},
            ))
    return issues