import pytest

from src.geometry.primitives import create_box
from src.geometry.transformations.translate import translate_model
from src.geometry.transformations.rotate import rotate_model

def test_translate_model():
    model = create_box(
        length=10,
        width=10,
        height=10,
    )

    translated_model = translate_model(
        model=model,
        x=10,
        y=20,
        z=30,
    )

    bounding_box = translated_model.val().BoundingBox()

    assert bounding_box.xmin == pytest.approx(5)
    assert bounding_box.xmax == pytest.approx(15)

    assert bounding_box.ymin == pytest.approx(15)
    assert bounding_box.ymax == pytest.approx(25)

    assert bounding_box.zmin == pytest.approx(25)
    assert bounding_box.zmax == pytest.approx(35)


def test_rotate_model():
    model = create_box(
        length=20,
        width=10,
        height=5,
    )

    rotated_model = rotate_model(
        model=model,
        axis_start=(0, 0, 0),
        axis_end=(0, 0, 1),
        angle=90,
    )

    bounding_box = rotated_model.val().BoundingBox()

    assert bounding_box.xlen == pytest.approx(10)
    assert bounding_box.ylen == pytest.approx(20)
    assert bounding_box.zlen == pytest.approx(5)

