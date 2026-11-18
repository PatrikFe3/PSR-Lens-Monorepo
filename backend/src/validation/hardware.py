"""Checks that every piece of hardware has a home and can work there."""
from src.core.issues import Issue


def check_hardware(spec, built, hardware, **_) -> list[Issue]:
    issues = []
    held = {hid for part in built.values() for hid, _ in part.holds}
    for h in spec.hardware:
        if h.id not in held:
            issues.append(Issue('unused_hardware', 'warning',
                                f'Hardware {h.id!r} ({h.ref}) is listed but no part holds it.',
                                hint='Add an enclosure or mount whose "hardware" parameter is this id.'))
    for pid, part in built.items():
        for hid, _ in part.holds:
            hw = hardware[hid]
            if hw.heat_sources and getattr(part.params, 'vents', True) is False:
                watts = sum(s.power_w for s in hw.heat_sources)
                issues.append(Issue('no_vents', 'warning',
                                    f'{pid} closes in {hid} ({watts:g} W) without vents.', part=pid,
                                    hint='Set "vents": true.'))
    return issues