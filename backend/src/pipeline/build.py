import json
from dataclasses import dataclass, field
from pathlib import Path

from src.assembly.collision import sweep_collisions
from src.assembly.manifest import body_to_glb, build_manifest
from src.assembly.solver import build_joints, solve
from src.core.issues import DesignError, Issue, has_errors
from src.manufacturing.plates import export_plate, plan_plates
from src.templates.base import BuildContext
from src.templates.features.interfaces import apply_interfaces
from src.validation.geometry import check_geometry
from src.validation.hardware import check_hardware
from src.validation.physics import check_stability
from src.validation.pipeline import Stage, run_stages
from src.validation.printability import check_printability
from src.validation.spec import check_spec


@dataclass
class BuildResult:
    design_id: str
    manifest: dict
    plates: dict
    files: dict[str, str]
    issues: list[Issue] = field(default_factory=list)


def _build_parts(spec, templates, ctx, assembly=None):
    built = {}
    for p in spec.parts:
        t = templates[p.template]
        try:
            params = t.parse(p.params)
            resolved = t.resolve(params, ctx, assembly) if t.needs_assembly else t.resolve(params, ctx)
        except ValueError as err:  # pydantic ValidationError is a ValueError too
            raise DesignError([Issue('bad_params', 'error', f'Part {p.id!r}: {err}', part=p.id,
                                     hint='Use "auto" when unsure.')]) from err
        built[p.id] = t.build(p.id, resolved, ctx)
    return built


def _stages() -> list[Stage]:
    return [
        Stage('printability', lambda **s: check_printability(s['built'], s['printer'])),
        Stage('geometry', lambda **s: check_geometry(s['built'])),
        Stage('hardware', lambda **s: check_hardware(s['spec'], s['built'], s['hardware'])),
        Stage('collisions', lambda **s: sweep_collisions(s['built'], s['joints'], s['hardware'])),
        Stage('physics', lambda **s: check_stability(s['built'], s['joints'], s['hardware'], s['material'])),
    ]


def validate_design(spec, catalog, templates, printer, material):
    """Build the parts in memory and run every check. Returns (built, joints, hardware, issues)."""
    issues = check_spec(spec, catalog, templates)
    if has_errors(issues):
        raise DesignError(issues)
    hardware = {h.id: catalog.hardware.get(h.ref) for h in spec.hardware}
    ctx = BuildContext(catalog, printer, material, hardware)

    built = _build_parts(spec, templates, ctx)
    joints = build_joints(spec, built, catalog)
    if any(templates[p.template].needs_assembly for p in spec.parts):
        built = _build_parts(spec, templates, ctx, assembly=solve(built, joints))
        joints = build_joints(spec, built, catalog)
    apply_interfaces(built, joints, ctx)

    issues += run_stages(_stages(), spec=spec, built=built, joints=joints, hardware=hardware,
                         printer=printer, material=material)
    if has_errors(issues):
        raise DesignError(issues)
    return built, joints, hardware, issues


def build_design(spec, catalog, templates, printer, material, out_dir, design_id,
                 plate_mode='spread') -> BuildResult:
    built, joints, hardware, issues = validate_design(spec, catalog, templates, printer, material)
    assembly = solve(built, joints)

    out_dir = Path(out_dir)
    meshes, hints, files = {}, {}, {}
    for pid, part in built.items():
        for name, body in part.bodies.items():
            key = f'{pid}.{name}'
            path = out_dir / 'meshes' / f'{key}.glb'
            meshes[key] = body_to_glb(body.shape, path)
            hints[key] = body.print_down
            files[key] = str(path)

    plates = plan_plates(meshes, hints, printer, material, mode=plate_mode)
    for i, plate in enumerate(plates['plates'], start=1):
        path = export_plate(meshes, plate, out_dir / 'plates' / f'plate_{i}.stl')
        files[f'plate_{i}'] = str(path)

    manifest = build_manifest(assembly, design_id, issues, hardware)
    (out_dir / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    (out_dir / 'spec.json').write_text(spec.model_dump_json(indent=1), encoding='utf-8')
    plates_json = {**plates, 'plates': [[{'key': i['key'], 'matrix': [round(float(v), 6) for v in
                                          i['matrix'].reshape(-1)]} for i in p] for p in plates['plates']]}
    (out_dir / 'plates.json').write_text(json.dumps(plates_json, indent=1), encoding='utf-8')
    files.update(manifest=str(out_dir / 'manifest.json'), spec=str(out_dir / 'spec.json'),
                 plates=str(out_dir / 'plates.json'))
    return BuildResult(design_id, manifest, plates_json, files, issues)