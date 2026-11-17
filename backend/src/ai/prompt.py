import json

RULES = '''You design 3D-printable assemblies.
Choose only hardware, templates, sites and interfaces listed below.
Never give coordinates or millimetre sizes unless a template parameter asks
for one; use "auto".
A connection {"a": "<part>.<site>", "b": "<part>.<site>"} attaches part b to part a.
Exactly one part is never the "b" of a connection: it is the base.
Revolute connections need "interface": "revolute_pin" and "range_deg": [low, high].
A part that holds hardware names it with its "hardware" parameter (the id from "hardware").
Write each guess you make into "assumptions" and each decision only the user
can make into "questions". Answer with JSON only.'''

EXAMPLE_SPEC = {
    'intent': 'Raspberry Pi case with a camera on a turning arm',
    'hardware': [
        {'id': 'pi', 'ref': 'raspberry_pi_4b'},
        {'id': 'cam', 'ref': 'rpi_camera_module_3'},
    ],
    'parts': [
        {'id': 'case', 'template': 'enclosure', 'params': {'hardware': 'pi', 'wall': 'auto',
                                                          'clearance': 'auto', 'vents': True}},
        {'id': 'arm', 'template': 'link', 'params': {'length': 'auto', 'width': 'auto', 'thickness': 'auto'}},
        {'id': 'camera_mount', 'template': 'sensor_mount',
         'params': {'hardware': 'cam', 'wall': 'auto', 'margin': 'auto'}},
    ],
    'connections': [
        {'a': 'case.top', 'b': 'arm.base', 'kind': 'revolute', 'interface': 'revolute_pin',
         'range_deg': [-90, 90], 'rest_deg': 0},
        {'a': 'arm.tip', 'b': 'camera_mount.base', 'kind': 'fixed', 'interface': 'screw_m2_5',
         'range_deg': None, 'rest_deg': 0},
    ],
    'assumptions': ['The arm turns 90 degrees each way.'],
    'questions': [],
}


def catalog_brief(catalog, templates) -> str:
    lines = ['Hardware:']
    lines += [f'- {h.id} ({h.category}): {h.description}' for h in catalog.hardware.all()]
    lines += ['Templates (sites in brackets):']
    lines += [f'- {t.name}: {t.description} [{", ".join(t.site_names)}]' for t in templates.values()]
    lines += ['Interfaces:']
    lines += [f'- {i.id} ({i.kind}): {i.description}' for i in catalog.interfaces.all()]
    return '\n'.join(lines)


def design_prompt(request: str, printer, brief: str, example: dict | None = None) -> str:
    example = EXAMPLE_SPEC if example is None else example
    return '\n\n'.join([RULES, brief,
                        f'Printer: {printer.name}, bed {printer.bed.width:g} x {printer.bed.depth:g} mm, '
                        f'height {printer.max_height:g} mm.',
                        'Example:\n' + json.dumps(example, indent=1),
                        'Request:\n' + request])


def revision_prompt(original: str, spec_json: str, issues_json: str) -> str:
    return (f'{original}\n\nYour previous design:\n{spec_json}\n\n'
            f'It failed these checks:\n{issues_json}\n\n'
            'Return the full corrected design. Change only what the issues require.')