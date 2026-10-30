import pytest
#pytest -v tests/test_primitives.py - command for run all tests from project root

from src.geometry.primitives import  (
    create_box,
    create_cylinder,
    create_sphere,
    create_torus,
    create_pipe,
    create_coil,
)

def test_create_box():
    model = create_box(10, 20, 30)

    assert model.val().Volume() == pytest.approx(6000)

def test_create_cylinder():
    model = create_cylinder(5, 10)

    assert model.val().Volume() == pytest.approx(
        3.141592653589793 * 25 * 10,
        rel=1e-5,
    )

def test_create_sphere():
    model = create_sphere(5)

    assert model.val().Volume() == pytest.approx(
        4 / 3 * 3.141592653589793 * 125,
        rel=1e-5,
    )

def test_create_torus():
    model = create_torus(5, 2)

    assert model.val().isValid()
    assert model.val().Volume() > 0

    expected_volume = 2 * (3.141592653589793 ** 2) * 5 * (2 ** 2)

    assert model.val().Volume() == pytest.approx(
        expected_volume,
        rel=1e-5
    )

def test_create_pipe():
    model = create_pipe(5, 3, 10)

    assert model.val().Volume() == pytest.approx(
        3.141592653589793 * (25 - 9) * 10,
        rel=1e-5,
    )

def test_create_coil():
    model = create_coil(
        radius=5,
        height=5,
        pitch=5,
        wire_radius=1,
    )

    assert model.val().Volume() > 0

def test_box_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        create_box(-10, 20, 30)

def test_pipe_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        create_pipe(3, 5, 10)

