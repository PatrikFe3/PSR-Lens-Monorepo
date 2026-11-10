import pytest

from src.geometry.generators.brick_generator import generate_brick

def test_generate_brick_4x2():
    brick = generate_brick(studs_x=4, studs_y=2)

    bounding_box = brick.val().BoundingBox()

    assert brick.val().isValid()
    assert bounding_box.xlen == pytest.approx(32)
    assert bounding_box.ylen == pytest.approx(16)
    assert bounding_box.zlen == pytest.approx(6.8)

def test_generate_brick_invalid_radius():
    with pytest.raises(ValueError):
        generate_brick(
            studs_x=2,
            studs_y=2,
            stud_radius=2.0,
            stud_inner_radius=2.0,
        )
