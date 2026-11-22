"""
    Sanity checks on the built solids.
"""
from src.core.issues import Issue
from src.geometry.kernel import kernel


def check_geometry(built, **_) -> list[Issue]:
    k = kernel()
    issues = []
    for pid, part in built.items():
        for name, body in part.bodies.items():
            volume = k.volume(body.shape)
            if volume <= 0.5:
                issues.append(Issue('empty_body', 'error', f'Body {pid}.{name} has no volume.', part=pid,
                                    hint='Check the template parameters.'))
    return issues