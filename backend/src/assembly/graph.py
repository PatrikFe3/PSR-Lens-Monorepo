"""The connection graph of a design: which part hangs on which."""
from collections import deque
from dataclasses import dataclass, field

from src.core.issues import Issue


@dataclass
class AssemblyTree:
    root: str | None
    parent: dict[str, object] = field(default_factory=dict)      # child id -> Connection
    children: dict[str, list[str]] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)               # parents before children


def assembly_tree(spec) -> tuple[AssemblyTree, list[Issue]]:
    """Build the parent/child tree and report every structural problem."""
    issues: list[Issue] = []
    part_ids = [p.id for p in spec.parts]
    known = set(part_ids)
    tree = AssemblyTree(root=None, children={pid: [] for pid in part_ids})

    for c in spec.connections:
        if c.parent not in known or c.child not in known:
            continue  # reported by the spec checker
        if c.child == c.parent:
            issues.append(Issue('self_connection', 'error', f'Part {c.child!r} is connected to itself.',
                                part=c.child, hint='Connect two different parts.'))
            continue
        if c.child in tree.parent:
            issues.append(Issue('multiple_parents', 'error',
                                f'Part {c.child!r} is the "b" of more than one connection.',
                                part=c.child, hint='Each part hangs on exactly one parent; swap a and b.'))
            continue
        tree.parent[c.child] = c
        tree.children[c.parent].append(c.child)

    roots = [pid for pid in part_ids if pid not in tree.parent]
    if not roots:
        issues.append(Issue('no_base', 'error', 'Every part is the "b" of a connection, so there is no base.',
                            hint='Exactly one part must never be a "b": it is the base.'))
        return tree, issues
    tree.root = roots[0]

    queue, seen = deque([tree.root]), {tree.root}
    while queue:
        pid = queue.popleft()
        tree.order.append(pid)
        for child in tree.children[pid]:
            if child not in seen:
                seen.add(child)
                queue.append(child)

    for pid in part_ids:
        if pid in seen:
            continue
        if pid in roots:
            issues.append(Issue('disconnected_part', 'error',
                                f'Part {pid!r} is not connected to the base {tree.root!r}.', part=pid,
                                hint='Add a connection with this part as "b".'))
        else:
            issues.append(Issue('cycle', 'error', f'Part {pid!r} is part of a connection loop.', part=pid,
                                hint='Connections must form a tree hanging from the base.'))
    return tree, issues