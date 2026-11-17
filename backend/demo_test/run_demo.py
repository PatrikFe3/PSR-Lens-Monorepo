"""Walk-through of the new design pipeline.

Run from the backend folder:

    python demo_test/run_demo.py                 # uses cadquery if installed, else the preview kernel
    python demo_test/run_demo.py --kernel preview
    python demo_test/run_demo.py --ollama "a raspberry pi case with a camera on a turning arm"

What it shows, step by step:
  1. the catalog (hardware, interfaces, printers, materials) and the part templates
  2. a valid design: Raspberry Pi case + turning arm + camera bracket, checked and built
     into GLB meshes (web viewer), STL build plates (printer) and a manifest
  3. a design that fails the checks (it would tip over) and the issues it reports
  4. the AI loop with a scripted "fake" LLM: bad answer -> issues fed back -> fixed answer
  5. optionally the same loop with your local Ollama model
All files go to demo_test/output/.
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from src.core.issues import DesignError  # noqa: E402
from src.geometry.kernel import set_kernel  # noqa: E402
from src.validation.physics import center_of_mass  # noqa: E402

OUTPUT = Path(__file__).resolve().parent / 'output'

TURRET = {
    'intent': 'Raspberry Pi 4 case with a camera on an arm that turns 90 degrees each way',
    'hardware': [
        {'id': 'pi', 'ref': 'raspberry_pi_4b'},
        {'id': 'cam', 'ref': 'rpi_camera_module_3'},
    ],
    'parts': [
        {'id': 'case', 'template': 'enclosure', 'params': {'hardware': 'pi'}},
        {'id': 'arm', 'template': 'link', 'params': {'length': 'auto'}},
        {'id': 'camera_mount', 'template': 'sensor_mount', 'params': {'hardware': 'cam'}},
    ],
    'connections': [
        {'a': 'case.top', 'b': 'arm.base', 'kind': 'revolute', 'interface': 'revolute_pin',
         'range_deg': [-90, 90]},
        {'a': 'arm.tip', 'b': 'camera_mount.base', 'kind': 'fixed', 'interface': 'screw_m2_5'},
    ],
    'assumptions': [],
    'questions': [],
}

# Same idea on a small pedestal with a 220 mm arm: the centre of mass leaves the base.
TOP_HEAVY = {
    'intent': 'Camera on a very long arm on a small base',
    'hardware': [{'id': 'cam', 'ref': 'rpi_camera_module_3'}],
    'parts': [
        {'id': 'base', 'template': 'pedestal', 'params': {'diameter': 50, 'height': 6}},
        {'id': 'arm', 'template': 'link', 'params': {'length': 220}},
        {'id': 'camera_mount', 'template': 'sensor_mount', 'params': {'hardware': 'cam'}},
    ],
    'connections': [
        {'a': 'base.top', 'b': 'arm.base', 'kind': 'revolute', 'interface': 'revolute_pin',
         'range_deg': [-45, 45]},
        {'a': 'arm.tip', 'b': 'camera_mount.base', 'kind': 'fixed', 'interface': 'screw_m2_5'},
    ],
    'assumptions': [],
    'questions': [],
}


def title(text):
    print('\n' + '=' * 78 + f'\n{text}\n' + '=' * 78)


class ScriptedLLM:
    """Stands in for Ollama: answers with prepared JSON, one answer per call."""

    def __init__(self, answers):
        self.answers, self.prompts = list(answers), []

    def generate(self, prompt, response_format=None):
        self.prompts.append(prompt)
        return json.dumps(self.answers.pop(0))


def show_issues(issues, indent='   '):
    for i in issues:
        where = f' [{i.part}]' if i.part else ''
        print(f'{indent}{i.severity.upper():7} {i.code}{where}: {i.message}')
        if i.hint:
            print(f'{indent}        hint: {i.hint}')


def step_catalog(service):
    title('1. Catalog and templates')
    for group, ids in service.catalog.summary().items():
        print(f'   {group:10} {", ".join(ids)}')
    print()
    for t in service.templates.values():
        params = ', '.join(t.Params.model_fields)
        print(f'   template {t.name:13} sites={t.site_names}  params=({params})')


def step_build(service):
    title('2. Build a valid design: Pi case + turning arm + camera bracket')
    start = time.time()
    result = service.build(TURRET, design_id='turret')
    print(f'   built in {time.time() - start:.1f} s with the "{service.kernel.name}" kernel')
    print(f'   warnings: {len(result.issues)}')
    show_issues(result.issues)

    from src.pipeline.build import validate_design
    from src.assembly.solver import solve
    printer, material = service._profiles()
    built, joints, hardware, _ = validate_design(service.parse_spec(TURRET), service.catalog,
                                                 service.templates, printer, material)
    for angle in (-90, 0, 90):
        com, mass = center_of_mass(solve(built, joints, {'arm': angle}), hardware, material.density_g_cm3)
        print(f'   arm at {angle:+4d} deg: mass {mass:5.0f} g, centre of mass x={com[0]:6.1f} y={com[1]:6.1f} mm')

    print('\n   parts in the manifest (what the web viewer loads):')
    for p in result.manifest['parts']:
        joint = p.get('joint')
        how = f'{joint["kind"]} via {joint["interface"]} on {p["parent"]}' if joint else 'base'
        print(f'     {p["id"]:13} {p["template"]:13} bodies={[b["name"] for b in p["bodies"]]}  {how}')
    print(f'\n   build plates for {result.plates["printer"]}: {len(result.plates["plates"])}')
    for n, plate in enumerate(result.plates['plates'], start=1):
        print(f'     plate {n}: {[i["key"] for i in plate]}')
    print('\n   files written:')
    for key, path in sorted(result.files.items()):
        print(f'     {key:16} {Path(path).relative_to(BACKEND)}')
    return result


def step_failure(service):
    title('3. A design that fails the checks (top-heavy arm)')
    try:
        service.build(TOP_HEAVY, design_id='top_heavy')
        print('   unexpectedly passed')
    except DesignError as err:
        print(f'   rejected with {len(err.issues)} issue(s):')
        show_issues(err.issues)


def step_ai_scripted(service):
    title('4. AI loop with a scripted LLM (no Ollama needed)')
    first = copy.deepcopy(TOP_HEAVY)
    fixed = copy.deepcopy(TOP_HEAVY)
    fixed['parts'][0]['params'] = {'diameter': 'auto', 'height': 'auto'}
    fixed['parts'][1]['params'] = {'length': 60}
    fixed['assumptions'] = ['Shortened the arm and used the default 90 mm base so it cannot tip over.']
    llm = ScriptedLLM([first, fixed])
    service.output_dir = OUTPUT / 'ai'
    spec, result = service.design_from_prompt('A camera on an arm that can turn 45 degrees each way.',
                                              llm=llm, log=lambda msg: print('   ' + msg))
    print(f'   LLM calls: {len(llm.prompts)}; the 2nd prompt contained the failed checks: '
          f'{"tips_over" in llm.prompts[1]}')
    print(f'   accepted design "{result.design_id}": arm length {spec.parts[1].params["length"]} mm')
    print(f'   assumptions: {spec.assumptions}')
    service.output_dir = OUTPUT


def step_ai_ollama(service, request):
    title('5. AI loop with your local Ollama model')
    from src.ai.orchestrator import NeedsInput
    from src.exceptions.ollama_exception import OllamaConnectionError
    try:
        spec, result = service.design_from_prompt(request, ask_user=False, log=lambda m: print('   ' + m))
        print(f'   built design {result.design_id}: {[p.id for p in spec.parts]}')
    except NeedsInput as err:
        print(f'   the model asks: {err.questions}')
    except DesignError as err:
        print('   the model did not produce a valid design in 3 rounds:')
        show_issues(err.issues)
    except OllamaConnectionError as err:
        print(f'   {err}')


def render(result, path):
    """Optional picture of the assembly (needs matplotlib)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        import numpy as np
    except ImportError:
        return None
    from src.manufacturing.export import read_glb
    colours = ['#8fa8c8', '#c8a08f', '#9fc88f', '#c8c08f']
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(projection='3d')
    points = []
    for n, part in enumerate(result.manifest['parts']):
        world = np.array(part['world']).reshape(4, 4)
        for body in part['bodies']:
            mesh = read_glb(Path(result.files[f'{part["id"]}.{body["name"]}'])).apply_transform(world)
            light = 0.55 + 0.45 * np.clip(mesh.face_normals @ np.array([0.3, -0.5, 0.8]), 0, 1)
            colour = np.array(matplotlib.colors.to_rgb(colours[n % len(colours)]))
            ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=light[:, None] * colour,
                                                 edgecolor='none'))
            points.append(mesh.vertices)
    pts = np.concatenate(points)
    centre, radius = (pts.min(0) + pts.max(0)) / 2, (pts.max(0) - pts.min(0)).max() / 2
    for axis, c in zip('xyz', centre):
        getattr(ax, f'set_{axis}lim')(c - radius, c + radius)
    ax.view_init(25, -60)
    ax.set_title(result.manifest['id'])
    fig.savefig(path, dpi=90)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--kernel', default='auto', choices=['auto', 'cadquery', 'preview'])
    parser.add_argument('--ollama', metavar='REQUEST', help='also run the AI loop against local Ollama')
    args = parser.parse_args()

    set_kernel(args.kernel)
    from src.services.design_service import DesignService
    service = DesignService(output_dir=OUTPUT)
    print(f'Backend: {BACKEND}\nKernel:  {service.kernel.name}'
          + ('' if service.kernel.exact else '  (approximate - install cadquery for exact solids)'))

    step_catalog(service)
    result = step_build(service)
    step_failure(service)
    step_ai_scripted(service)
    if args.ollama:
        step_ai_ollama(service, args.ollama)

    picture = render(result, OUTPUT / 'turret.png')
    title('Done')
    print(f'   outputs: {OUTPUT}')
    if picture:
        print(f'   picture: {picture}')
    print('   open the plate STL files in PrusaSlicer / Cura; the .glb files in any glTF viewer.')


if __name__ == '__main__':
    main()
