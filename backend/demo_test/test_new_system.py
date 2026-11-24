"""

"""
import copy
import json
from pathlib import Path

import numpy as np
import pytest

from demo_test.run_demo import TOP_HEAVY, TURRET, ScriptedLLM
from src.ai.orchestrator import DesignAgent, NeedsInput
from src.ai.schema import design_spec_model
from src.assembly.collision import sweep_collisions
from src.assembly.solver import build_joints, solve
from src.catalog.loader import load_catalog
from src.catalog.registry import CatalogError
from src.core.frames import rot_z
from src.core.issues import DesignError, Issue
from src.core.spec import DesignSpec
from src.geometry.kernel import kernel
from src.geometry.mesh import TriMesh
from src.manufacturing.export import read_glb, read_stl_triangle_count, write_glb, write_stl
from src.manufacturing.orientation import orient
from src.manufacturing.packing import Item, _distribute, _pack, layout, usable_rect
from src.manufacturing.plates import plan_plates
from src.pipeline.build import build_design, validate_design
from src.services.design_service import DesignService
from src.templates.registry import default_templates
from src.validation.pipeline import Stage, issues_for_ai, run_stages
from src.validation.spec import check_spec

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def catalog():
    return load_catalog(BACKEND / 'catalogs')


@pytest.fixture
def templates():
    return default_templates()


@pytest.fixture
def printer(catalog):
    return catalog.printers.get('prusa_mk4s')


@pytest.fixture
def pla(catalog):
    return catalog.materials.get('pla')


def box_mesh(x, y, z) -> TriMesh:
    v = np.array([[i, j, k] for i in (0, x) for j in (0, y) for k in (0, z)], dtype=float)
    f = [[0, 2, 3], [0, 3, 1], [4, 5, 7], [4, 7, 6], [0, 1, 5], [0, 5, 4],
         [2, 6, 7], [2, 7, 3], [0, 4, 6], [0, 6, 2], [1, 3, 7], [1, 7, 5]]
    return TriMesh(v, np.array(f)[:, ::-1])  # outward-facing triangles


# ------------------------------------------------------------------ catalog
def test_catalog_loads_every_yaml_file(catalog):
    assert 'raspberry_pi_4b' in catalog.hardware
    assert catalog.interfaces.ids() == ['dovetail', 'revolute_pin', 'screw_m2_5', 'stud_grid']
    assert set(catalog.printers.ids()) == {'creality_ender_6', 'prusa_mini_plus', 'prusa_mk4s'}
    assert catalog.interfaces.get('revolute_pin').female_feature == 'bore_boss'


def test_empty_yaml_file_is_a_clear_error(tmp_path):
    for group in ('hardware', 'interfaces', 'printers', 'materials'):
        (tmp_path / group).mkdir()
    (tmp_path / 'materials' / 'abs.yaml').write_text('', encoding='utf-8')
    with pytest.raises(CatalogError, match='empty'):
        load_catalog(tmp_path)


def test_misspelled_yaml_key_is_rejected(tmp_path):
    for group in ('hardware', 'interfaces', 'printers', 'materials'):
        (tmp_path / group).mkdir()
    (tmp_path / 'printers' / 'p.yaml').write_text(
        'id: p\nname: P\nbed: {width: 200, depth: 200}\nmax_height: 200\nnozzle_height: 0.4\n'
        'fit_classes: {press: 0.05, snug: 0.15, sliding: 0.25, loose: 0.4}\n', encoding='utf-8')
    with pytest.raises(CatalogError, match='nozzle_height'):
        load_catalog(tmp_path)


def test_bed_exclusion_shrinks_usable_area(printer):
    assert usable_rect(printer.bed) == (4, 8, 246, 206)


# ------------------------------------------------------------------ packing
def test_first_item_is_packed():
    plates = _pack([Item('a', 50, 40)], 242, 198, 6)
    assert len(plates) == 1 and plates[0][0].items[0][0].key == 'a'


def test_items_that_do_not_fit_open_a_new_plate():
    plates = _pack([Item(f'p{i}', 150, 150) for i in range(3)], 200, 200, 6)
    assert len(plates) == 3


def test_shelf_depth_counts_gaps_between_shelves():
    # two 95 mm shelves + one 6 mm gap = 196 mm fits a 200 mm bed; a third shelf does not
    plates = _pack([Item('a', 150, 95), Item('b', 150, 95), Item('c', 150, 95)], 200, 200, 6)
    assert [len(p) for p in plates] == [2, 1]


def test_distribute_returns_numbers_when_space_is_tight():
    offsets = _distribute(100, [30, 30, 30], 6, 'spread')
    assert all(isinstance(o, float) for o in offsets)
    assert offsets[0] == 0.0 and offsets[-1] + 30 == pytest.approx(100)


def test_layout_keeps_parts_on_bed_and_apart(printer):
    rng = np.random.default_rng(3)
    items = [Item(f'p{i}', *rng.uniform(10, 90, 2)) for i in range(14)]
    placed = layout(items, printer)
    assert {p.key for p in placed} == {i.key for i in items}
    x0, y0, x1, y1 = usable_rect(printer.bed)
    for p in placed:
        assert x0 - 1e-6 <= p.x and p.x + p.w <= x1 + 1e-6 and y0 - 1e-6 <= p.y and p.y + p.d <= y1 + 1e-6
    for a in placed:
        for b in placed:
            if a is b or a.plate != b.plate:
                continue
            apart = (a.x + a.w <= b.x + 1e-6 or b.x + b.w <= a.x + 1e-6 or
                     a.y + a.d <= b.y + 1e-6 or b.y + b.d <= a.y + 1e-6)
            assert apart, (a, b)


# ------------------------------------------------------------------ orientation and plates
def test_orient_with_hint_returns_a_matrix_that_sits_on_the_origin():
    m = orient(box_mesh(10, 20, 30), '+X')
    assert m is not None
    lo, hi = box_mesh(10, 20, 30).apply_transform(m).bounds
    assert np.allclose(lo, 0) and hi[2] == pytest.approx(10)


def test_orient_lays_a_standing_plate_flat():
    m = orient(box_mesh(2, 60, 40), None)
    lo, hi = box_mesh(2, 60, 40).apply_transform(m).bounds
    assert hi[2] - lo[2] == pytest.approx(2)


def test_rotated_parts_with_brim_stay_inside_their_slot(printer, pla):
    material = pla.model_copy(update={'brim': 3.0})
    meshes = {f'p{i}.main': box_mesh(30, 140, 10) for i in range(3)}
    plan = plan_plates(meshes, {k: '-Z' for k in meshes}, printer, material)
    x0, y0, x1, y1 = plan['usable']
    for plate in plan['plates']:
        boxes = [meshes[i['key']].copy().apply_transform(i['matrix']).bounds for i in plate]
        for lo, hi in boxes:
            assert x0 - 1e-6 <= lo[0] and hi[0] <= x1 + 1e-6 and lo[2] == pytest.approx(0)


def test_too_tall_part_is_an_issue_not_a_crash(printer, pla):
    with pytest.raises(DesignError) as err:
        plan_plates({'tower.main': box_mesh(250, 250, 300)}, {'tower.main': '-Z'}, printer, pla)
    codes = {i.code for i in err.value.issues}
    assert 'part_too_tall' in codes and all(i.part == 'tower' for i in err.value.issues)


def test_stl_and_glb_round_trip(tmp_path):
    mesh = box_mesh(10, 20, 30)
    assert read_stl_triangle_count(write_stl(mesh, tmp_path / 'a.stl')) == 12
    back = read_glb(write_glb(mesh, tmp_path / 'a.glb'))
    assert np.allclose(back.vertices, mesh.vertices) and back.volume == pytest.approx(6000)


# ------------------------------------------------------------------ validation helpers
def test_run_stages_collects_and_stops_at_first_error():
    calls = []
    stages = [Stage('a', lambda **s: calls.append('a') or [Issue('w', 'warning', 'w')]),
              Stage('b', lambda **s: calls.append('b') or [Issue('e', 'error', 'e')]),
              Stage('c', lambda **s: calls.append('c') or [])]
    issues = run_stages(stages, x=1)
    assert calls == ['a', 'b'] and [i.code for i in issues] == ['w', 'e']


def test_issues_for_ai_keeps_only_errors():
    text = issues_for_ai([Issue('tips_over', 'error', 'falls', part='base'), Issue('x', 'warning', 'w')])
    assert json.loads(text) == [{'code': 'tips_over', 'part': 'base', 'message': 'falls'}]


def test_spec_checker_finds_every_kind_of_mistake(catalog, templates):
    spec = DesignSpec.model_validate({
        'intent': 'broken',
        'hardware': [{'id': 'cam', 'ref': 'no_such_board'}],
        'parts': [{'id': 'a', 'template': 'link', 'params': {'lenght': 5}},
                  {'id': 'b', 'template': 'widget'},
                  {'id': 'c', 'template': 'link'}],
        'connections': [{'a': 'a.tip', 'b': 'c.top', 'kind': 'revolute', 'interface': 'screw_m2_5'}],
    })
    codes = {i.code for i in check_spec(spec, catalog, templates)}
    assert {'unknown_hardware', 'bad_params', 'unknown_template', 'unknown_site',
            'interface_kind', 'missing_range'} <= codes


def test_valid_spec_has_no_issues(catalog, templates):
    assert check_spec(DesignSpec.model_validate(TURRET), catalog, templates) == []


# ------------------------------------------------------------------ assembly
def _built(spec_dict, catalog, templates, printer, pla):
    return validate_design(DesignSpec.model_validate(spec_dict), catalog, templates, printer, pla)


def test_mated_sites_touch_and_face_each_other(catalog, templates, printer, pla):
    built, joints, _, _ = _built(TURRET, catalog, templates, printer, pla)
    for angle in (-90, 30, 90):
        a = solve(built, joints, {'arm': angle})
        parent = a.site_world('case', 'top')
        child = a.site_world('arm', 'base')
        gap = catalog.interfaces.get('revolute_pin').gap
        assert np.allclose(child[:3, 3], parent[:3, 3] + gap * parent[:3, 2])
        assert np.allclose(child[:3, 2], -parent[:3, 2])
        assert np.allclose(child[:3, 0], (rot_z(angle) @ parent)[:3, 0])


def test_angle_outside_range_is_rejected(catalog, templates, printer, pla):
    built, joints, _, _ = _built(TURRET, catalog, templates, printer, pla)
    with pytest.raises(ValueError, match='outside its range'):
        solve(built, joints, {'arm': 120})


def test_collision_sweep_finds_misaligned_studs(catalog, templates, printer, pla):
    spec = DesignSpec.model_validate({
        'intent': 'two bricks', 'parts': [{'id': 'b1', 'template': 'brick'}, {'id': 'b2', 'template': 'brick'}],
        'connections': [{'a': 'b1.top', 'b': 'b2.bottom', 'kind': 'fixed', 'interface': 'stud_grid',
                         'rest_deg': 45}]})
    with pytest.raises(DesignError) as err:
        validate_design(spec, catalog, templates, printer, pla)
    assert [i.code for i in err.value.issues] == ['collision']


def test_aligned_studs_do_not_collide(catalog, templates, printer, pla):
    spec = DesignSpec.model_validate({
        'intent': 'two bricks', 'parts': [{'id': 'b1', 'template': 'brick'}, {'id': 'b2', 'template': 'brick'}],
        'connections': [{'a': 'b1.top', 'b': 'b2.bottom', 'kind': 'fixed', 'interface': 'stud_grid'}]})
    built, joints, hardware, issues = validate_design(spec, catalog, templates, printer, pla)
    assert sweep_collisions(built, joints, hardware) == []


def test_top_heavy_design_tips_over(catalog, templates, printer, pla):
    with pytest.raises(DesignError) as err:
        _built(TOP_HEAVY, catalog, templates, printer, pla)
    assert {i.code for i in err.value.issues} == {'tips_over'}


# ------------------------------------------------------------------ full pipeline (both kernels)
def test_build_design_end_to_end(any_kernel, catalog, templates, printer, pla, tmp_path):
    spec = DesignSpec.model_validate(TURRET)
    result = build_design(spec, catalog, templates, printer, pla, tmp_path, 'turret')

    for key in ('case.main', 'case.lid', 'arm.main', 'camera_mount.main'):
        mesh = read_glb(result.files[key])
        assert len(mesh.faces) > 0 and mesh.volume > 0  # closed, outward-facing surface
    assert read_stl_triangle_count(result.files['plate_1']) > 0
    manifest = json.loads(Path(result.files['manifest']).read_text())
    assert manifest == result.manifest and manifest['root'] == 'case'

    # the viewer formula reproduces the solver's world matrices
    parts = {p['id']: p for p in manifest['parts']}
    for p in manifest['parts']:
        if 'joint' not in p:
            continue
        j = p['joint']
        parent_world = np.array(parts[p['parent']]['world']).reshape(4, 4)
        world = (parent_world @ np.array(j['parent_frame']).reshape(4, 4) @ rot_z(j['value'])
                 @ np.array(j['child_offset']).reshape(4, 4))
        assert np.allclose(world, np.array(p['world']).reshape(4, 4), atol=1e-5)


def test_enclosure_fits_the_board(any_kernel, catalog, templates, printer, pla):
    built, *_ = _built(TURRET, catalog, templates, printer, pla)
    lo, hi = kernel().bounds(built['case'].bodies['main'].shape)
    board = catalog.hardware.get('raspberry_pi_4b').board
    assert hi[0] - lo[0] > board.length + 2 * printer.default_wall
    assert hi[1] - lo[1] > board.width + 2 * printer.default_wall


# ------------------------------------------------------------------ AI loop
def test_schema_only_allows_catalog_choices(catalog, templates):
    model = design_spec_model(catalog, templates)
    good = copy.deepcopy(TURRET)
    model.model_validate(good)
    bad = copy.deepcopy(TURRET)
    bad['parts'][0]['template'] = 'spaceship'
    with pytest.raises(ValueError):
        model.model_validate(bad)
    bad = copy.deepcopy(TURRET)
    bad['connections'][0]['kind'] = 'fied'
    with pytest.raises(ValueError):
        model.model_validate(bad)


def _agent(service, answers, rounds=3):
    llm = ScriptedLLM(answers)
    return service.agent(llm, max_rounds=rounds), llm


@pytest.fixture
def service(tmp_path, catalog):
    return DesignService(catalog=catalog, output_dir=tmp_path, kernel_name='preview')


def test_agent_feeds_failures_back_and_retries(service):
    fixed = copy.deepcopy(TOP_HEAVY)
    fixed['parts'][1]['params'] = {'length': 60}
    fixed['parts'][0]['params'] = {}
    agent, llm = _agent(service, [TOP_HEAVY, fixed])
    spec, result = agent.design('make it')
    assert len(llm.prompts) == 2 and 'tips_over' in llm.prompts[1]
    assert Path(result.files['manifest']).exists()


def test_agent_retries_after_invalid_json(service):
    agent, llm = _agent(service, [{'intent': 'x'}, TURRET])
    agent.design('make it')
    assert 'bad_spec' in llm.prompts[1]


def test_agent_gives_up_after_max_rounds(service):
    agent, _ = _agent(service, [TOP_HEAVY] * 2, rounds=2)
    with pytest.raises(DesignError):
        agent.design('make it')


def test_agent_stops_for_user_questions(service):
    question = dict(TURRET, questions=['Which way should the camera face?'])
    agent, _ = _agent(service, [question])
    with pytest.raises(NeedsInput) as err:
        agent.design('make it')
    assert err.value.questions == ['Which way should the camera face?']


def test_prompt_lists_catalog_and_templates(service):
    text = service.prompt_for('a camera arm')
    assert 'raspberry_pi_4b' in text and 'Templates' in text and 'revolute_pin' in text


# ------------------------------------------------------------------ settings and API
def test_settings_accept_old_timeout_name(monkeypatch):
    from src.core.settings import get_settings
    monkeypatch.delenv('OLLAMA_TIMEOUT', raising=False)
    monkeypatch.setenv('TIMEOUT', '42')
    assert get_settings().ollama_timeout == 42.0


def test_api_builds_and_serves_files(monkeypatch, tmp_path):
    pytest.importorskip('fastapi')
    pytest.importorskip('httpx')
    from fastapi.testclient import TestClient

    monkeypatch.setenv('PSR_OUTPUT_DIR', str(tmp_path))
    from src.api import routes
    routes.service.cache_clear()
    from src.api.app import app
    client = TestClient(app)

    assert client.get('/health').json()['status'] == 'ok'
    assert 'templates' in client.get('/catalog').json()
    ok = client.post('/designs', json={'spec': TURRET})
    assert ok.status_code == 200, ok.text
    design_id = ok.json()['design_id']
    assert client.get(f'/designs/{design_id}/manifest').json()['root'] == 'case'
    assert client.get(f'/designs/{design_id}/meshes/arm.main.glb').content[:4] == b'glTF'
    assert client.get(f'/designs/{design_id}/plates/1').status_code == 200
    bad = client.post('/designs', json={'spec': TOP_HEAVY})
    assert bad.status_code == 422 and bad.json()['issues'][0]['code'] == 'tips_over'
    routes.service.cache_clear()
