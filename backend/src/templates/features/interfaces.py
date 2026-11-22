"""
Joint features: the geometry an interface adds to the two parts it connects.
"""
from __future__ import annotations

import numpy as np

from src.core.frames import translate
from src.core.issues import Issue
from src.geometry.kernel import kernel

# Maps site coordinates of a prism (x = width, y = depth, z = extrusion) so that
# the extrusion runs along the site's X and the depth along the site's Z.
_PRISM_TO_SITE = np.array([[0.0, 0.0, 1.0, 0.0],
                           [1.0, 0.0, 0.0, 0.0],
                           [0.0, 1.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0, 1.0]])


def _union(shapes):
    k = kernel()
    shapes = [s for s in shapes if s is not None]
    if not shapes:
        return None
    out = shapes[0]
    for s in shapes[1:]:
        out = k.fuse(out, s)
    return out

def _pin_boss(p, c):
    k = kernel()
    boss = k.cylinder(p['boss_diameter'] / 2, p['boss_height'] + 0.5, (0, 0, -0.5))
    pin = k.cylinder(p['pin_diameter'] / 2, p['pin_length'] + 0.5, (0, 0, p['boss_height'] - 0.5))
    return k.fuse(boss, pin), None


def _pilot_holes(p, c, pilot):
    k = kernel()
    s = p['spacing'] / 2
    holes = [k.cylinder(pilot / 2, p['length'] + 0.2, (x, 0, -p['length'])) for x in (-s, s)]
    return None, _union(holes)


def _trapezoid(p, grow=0.0, mirror=False):
    wb, wt, d = p['width_base'] / 2 + grow, p['width_top'] / 2 + grow, p['depth'] + grow
    pts = [(-wb, 0.0), (wb, 0.0), (wt, d), (-wt, d)]
    if mirror:
        pts = [(x, -y) for x, y in pts]
    return pts


def _dovetail_tongue(p, c):
    k = kernel()
    body = k.prism(_trapezoid(p), p['length'])
    base = k.prism([(-p['width_base'] / 2, -0.5), (p['width_base'] / 2, -0.5),
                    (p['width_base'] / 2, 0.01), (-p['width_base'] / 2, 0.01)], p['length'])
    shape = k.fuse(body, base)
    return k.transform(shape, _PRISM_TO_SITE @ translate(0, 0, -p['length'] / 2)), None


def _studs(p, c):
    k = kernel()
    nx, ny, pitch = int(p['count_x']), int(p['count_y']), p['pitch']
    studs = [k.cylinder(p['stud_diameter'] / 2, p['stud_height'] + 0.5,
                        ((i - (nx - 1) / 2) * pitch, (j - (ny - 1) / 2) * pitch, -0.5))
             for i in range(nx) for j in range(ny)]
    return _union(studs), None


def _bore(p, c):
    k = kernel()
    depth = p['pin_length'] + c
    return None, k.cylinder(p['pin_diameter'] / 2 + c, depth + 0.5, (0, 0, -depth))


def _clearance_holes(p, c):
    k = kernel()
    s = p['spacing'] / 2
    holes = [k.cylinder(p['screw_diameter'] / 2 + c, p['length'] + 0.5, (x, 0, -p['length']))
             for x in (-s, s)]
    return None, _union(holes)


def _dovetail_slot(p, c):
    k = kernel()
    long = dict(p, length=p['length'] + 40.0)  # open-ended so the tongue can slide in
    slot = k.prism(_trapezoid(long, grow=c, mirror=True), long['length'])
    mouth = k.prism([(-p['width_base'] / 2 - c, -0.01), (p['width_base'] / 2 + c, -0.01),
                     (p['width_base'] / 2 + c, 0.5), (-p['width_base'] / 2 - c, 0.5)], long['length'])
    shape = k.fuse(slot, mouth)
    return None, k.transform(shape, _PRISM_TO_SITE @ translate(0, 0, -long['length'] / 2))


def _sockets(p, c):
    k = kernel()
    nx, ny, pitch = int(p['count_x']), int(p['count_y']), p['pitch']
    depth = p['stud_height'] + c
    holes = [k.cylinder(p['stud_diameter'] / 2 + c, depth + 0.5,
                        ((i - (nx - 1) / 2) * pitch, (j - (ny - 1) / 2) * pitch, -depth))
             for i in range(nx) for j in range(ny)]
    return None, _union(holes)

"""
Return: (add, cut) in site coordinates for a named feature.
"""
def feature_shapes(feature: str, interface, ctx):

    p = interface.params
    c = ctx.clearance(interface.fit)
    if feature == 'pin_boss':
        return _pin_boss(p, c)
    if feature == 'bore_boss':
        return _bore(p, c)
    if feature == 'pilot_holes':
        screw = 'M' + format(p['screw_diameter'], 'g')
        return _pilot_holes(p, c, ctx.pilot_diameter(screw, p['screw_diameter'] * 0.85))
    if feature == 'clearance_holes':
        return _clearance_holes(p, c)
    if feature == 'dovetail_tongue':
        return _dovetail_tongue(p, c)
    if feature == 'dovetail_slot':
        return _dovetail_slot(p, c)
    if feature == 'studs':
        return _studs(p, c)
    if feature == 'stud_sockets':
        return _sockets(p, c)
    raise ValueError(f'Unknown interface feature {feature!r} (interface {interface.id}).')


_FACE = {'+X': (1, 0, 0), '-X': (-1, 0, 0), '+Y': (0, 1, 0), '-Y': (0, -1, 0), '+Z': (0, 0, 1), '-Z': (0, 0, -1)}


def _apply(part, site_name: str, feature: str, interface, ctx) -> None:
    k = kernel()
    site = part.sites[site_name]
    body = part.bodies[site.body]
    add, cut = feature_shapes(feature, interface, ctx)
    m = site.frame.matrix()
    if add is not None:
        body.shape = k.fuse(body.shape, k.transform(add, m))
        face = _FACE.get(body.print_down or '')
        if face is not None and np.dot(m[:3, 2], face) > 0.99:
            # The feature sticks out of the face this body would be printed on.
            part.notes.append(Issue(
                'print_orientation_changed', 'warning',
                f'{part.id}.{site.body}: the {interface.id} feature is on the face it was meant to be '
                f'printed on ({body.print_down}); the print orientation is chosen automatically.',
                part=part.id, site=site_name, hint='Check the slicer preview for supports.'))
            body.print_down = None
    if cut is not None:
        body.shape = k.cut(body.shape, k.transform(cut, m))


def apply_interfaces(built: dict, joints: dict, ctx) -> None:
    for joint in joints.values():
        if joint.interface is None:
            continue
        _apply(built[joint.parent], joint.parent_site, joint.interface.male_feature, joint.interface, ctx)
        _apply(built[joint.child], joint.child_site, joint.interface.female_feature, joint.interface, ctx)
