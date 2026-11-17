"""Printer-related checks that do not need the plate layout."""
from src.core.issues import Issue


def check_printability(built, printer, **_) -> list[Issue]:
    issues = []
    for pid, part in built.items():
        issues += list(getattr(part, 'notes', []))
        wall = getattr(part.params, 'wall', None)
        if isinstance(wall, (int, float)) and wall < printer.min_wall:
            issues.append(Issue(
                'wall_too_thin', 'error',
                f'{pid}: wall {wall:g} mm is thinner than {printer.min_wall:g} mm '
                f'({printer.min_wall_lines} lines of a {printer.nozzle_diameter:g} mm nozzle).',
                part=pid, hint='Use "auto" for the wall.'))
        for field in ('thickness', 'height'):
            value = getattr(part.params, field, None)
            if isinstance(value, (int, float)) and value < printer.min_wall:
                issues.append(Issue('too_thin', 'error', f'{pid}: {field} {value:g} mm is too thin to print.',
                                    part=pid, hint=f'Use at least {printer.min_wall:g} mm or "auto".'))
    return issues