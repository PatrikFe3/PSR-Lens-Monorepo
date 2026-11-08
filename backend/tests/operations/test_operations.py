import pytest
import cadquery as cq

from src.geometry.operations.boolean import (
    union_models,
    cut_model,
    intersect_models,
)

def test_union_models():
    model_a = cq.Workplane("XY").box(10, 10, 10)
    model_b = cq.Workplane("XY").box(10, 10, 10).translate((5, 0, 0))

    result = union_models(model_a, model_b)

    assert result.val().isValid()
    assert result.val().Volume() == pytest.approx(1500)

def test_cut_model():
    model_a = cq.Workplane("XY").box(10, 10, 10)
    model_b = cq.Workplane("XY").box(5, 5, 5)

    result = cut_model(model_a, model_b)

    assert result.val().isValid()
    assert result.val().Volume() == pytest.approx(875)

def test_intersect_models():
    model_a = cq.Workplane("XY").box(10, 10, 10)
    model_b = cq.Workplane("XY").box(5, 5, 5)

    result = intersect_models(model_a, model_b)

    assert result.val().isValid()
    assert result.val().Volume() == pytest.approx(125)