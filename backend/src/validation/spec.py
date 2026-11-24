"""
    Checks on a DesignSpec before any geometry is built.
"""
from pydantic import ValidationError

from src.assembly.graph import assembly_tree
from src.core.issues import Issue


def _err(code, message, part=None, site=None, hint=None, **data) -> Issue:
    return Issue(code, 'error', message, part=part, site=site, hint=hint, data=data)


def check_spec(spec, catalog, templates) -> list[Issue]:
    issues: list[Issue] = []

    hw_ids = [h.id for h in spec.hardware]
    for dup in sorted({i for i in hw_ids if hw_ids.count(i) > 1}):
        issues.append(_err('duplicate_hardware_id', f'Hardware id {dup!r} is used twice.'))
    for h in spec.hardware:
        if h.ref not in catalog.hardware:
            issues.append(_err('unknown_hardware', f'Hardware {h.id!r} refers to unknown {h.ref!r}.',
                               hint=f'Choose one of {catalog.hardware.ids()}.'))
    hw_by_id = {h.id: h for h in spec.hardware}

    part_ids = [p.id for p in spec.parts]
    if not part_ids:
        issues.append(_err('no_parts', 'The design has no parts.'))
    for dup in sorted({i for i in part_ids if part_ids.count(i) > 1}):
        issues.append(_err('duplicate_part_id', f'Part id {dup!r} is used twice.', part=dup))
    held_by: dict[str, str] = {}
    for p in spec.parts:
        template = templates.get(p.template)
        if template is None:
            issues.append(_err('unknown_template', f'Part {p.id!r} uses unknown template {p.template!r}.',
                               part=p.id, hint=f'Choose one of {sorted(templates)}.'))
            continue
        try:
            params = template.parse(p.params)
        except ValidationError as err:
            for e in err.errors():
                field = '.'.join(map(str, e['loc']))
                issues.append(_err('bad_params', f'Part {p.id!r}, parameter {field}: {e["msg"]}.',
                                   part=p.id, hint='Use "auto" when unsure.'))
            continue
        hw_id = getattr(params, 'hardware', None)
        if hw_id is None:
            continue
        if hw_id not in hw_by_id:
            issues.append(_err('unknown_hardware_use', f'Part {p.id!r} holds {hw_id!r}, which is not in '
                               f'the hardware list.', part=p.id, hint=f'Use one of {sorted(hw_by_id)}.'))
            continue
        if hw_id in held_by:
            issues.append(_err('hardware_held_twice', f'Hardware {hw_id!r} is held by both '
                               f'{held_by[hw_id]!r} and {p.id!r}.', part=p.id))
        held_by[hw_id] = p.id
        ref = hw_by_id[hw_id].ref
        if ref in catalog.hardware and template.hardware_categories:
            category = catalog.hardware.get(ref).category
            if category not in template.hardware_categories:
                issues.append(_err('wrong_hardware_category',
                                   f'Template {template.name!r} cannot hold {ref!r} ({category}).',
                                   part=p.id, hint=f'It holds: {list(template.hardware_categories)}.'))

    templates_by_part = {p.id: templates.get(p.template) for p in spec.parts}
    used_sites: dict[str, int] = {}
    for c in spec.connections:
        for ref in (c.a, c.b):
            used_sites[ref] = used_sites.get(ref, 0) + 1
        ok = True
        for ref, role in ((c.a, 'a'), (c.b, 'b')):
            if '.' not in ref:
                issues.append(_err('bad_site_ref', f'Connection {role}={ref!r} must look like "part.site".'))
                ok = False
                continue
            pid, site = ref.split('.', 1)
            if pid not in templates_by_part:
                issues.append(_err('unknown_part', f'Connection {role}={ref!r}: no part {pid!r}.'))
                ok = False
            elif templates_by_part[pid] is not None and site not in templates_by_part[pid].sites:
                issues.append(_err('unknown_site', f'Part {pid!r} has no site {site!r}.', part=pid, site=site,
                                   hint=f'Sites: {templates_by_part[pid].site_names}.'))
                ok = False

        if c.interface:
            if c.interface not in catalog.interfaces:
                issues.append(_err('unknown_interface', f'Unknown interface {c.interface!r}.',
                                   hint=f'Choose one of {catalog.interfaces.ids()}.'))
                ok = False
            else:
                iface = catalog.interfaces.get(c.interface)
                if iface.kind != c.kind:
                    issues.append(_err('interface_kind', f'Interface {iface.id!r} is {iface.kind}, but the '
                                       f'connection {c.a} -> {c.b} is {c.kind}.', part=c.child))
                if ok:
                    for ref in (c.a, c.b):
                        pid, site = ref.split('.', 1)
                        t = templates_by_part[pid]
                        if t is not None and c.interface not in t.sites[site]:
                            issues.append(_err('interface_not_accepted', f'Site {ref!r} does not accept '
                                               f'{c.interface!r}.', part=pid, site=site,
                                               hint=f'It accepts {list(t.sites[site])}.'))
        elif c.kind == 'revolute':
            issues.append(_err('missing_interface', f'Revolute connection {c.a} -> {c.b} needs an interface.',
                               part=c.child, hint='Use "revolute_pin".'))

        if c.kind == 'revolute':
            if c.range_deg is None:
                issues.append(_err('missing_range', f'Revolute connection {c.a} -> {c.b} needs range_deg.',
                                   part=c.child, hint='For example [-90, 90].'))
            else:
                lo, hi = c.range_deg
                if lo >= hi:
                    issues.append(_err('bad_range', f'range_deg {list(c.range_deg)} must go from low to high.',
                                       part=c.child))
                elif not lo <= c.rest_deg <= hi:
                    issues.append(_err('bad_rest', f'rest_deg {c.rest_deg} is outside range_deg '
                                       f'{list(c.range_deg)}.', part=c.child))
        elif c.range_deg is not None:
            issues.append(Issue('range_ignored', 'warning', f'Fixed connection {c.a} -> {c.b} ignores range_deg.',
                                part=c.child))

    for ref, count in used_sites.items():
        if count > 1:
            issues.append(_err('site_reused', f'Site {ref!r} is used by {count} connections.',
                               part=ref.split('.', 1)[0], hint='Use one connection per site.'))

    if part_ids and not any(i.code in ('unknown_part', 'bad_site_ref') for i in issues):
        _, tree_issues = assembly_tree(spec)
        issues += tree_issues

    return issues
