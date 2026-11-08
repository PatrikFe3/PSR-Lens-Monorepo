import pytest

from src.assembly import (
    AssemblyPlan,
    AssemblyInstruction,
    validate_assembly_plan,
)

@pytest.fixture
def valid_plan():
    return AssemblyPlan(
        name="Simple Robot",
        instructions=[
            AssemblyInstruction(
                component_id="base",
                component_type="brick_4x2",
            ),
            AssemblyInstruction(
                component_id="body",
                component_type="brick_2x2",
                parent_id="base",
                attachment="top",
            ),
            AssemblyInstruction(
                component_id="head",
                component_type="brick_2x4",
                parent_id="body",
                attachment="top",
            ),
        ]
    )

def test_validate_assembly_plan(valid_plan):
    result = validate_assembly_plan(valid_plan)

    assert result is None

def test_empty_assembly_plan():
    plan = AssemblyPlan(
        name="Empty",
        instructions=[],
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_assembly_plan(plan)

def test_component_without_id():
    plan = AssemblyPlan(
        name="Invalid Plan",
        instructions=[
            AssemblyInstruction(
                component_id="",
                component_type="brick_2x2",
            )
        ],
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        validate_assembly_plan(plan)

def test_duplicate_component_ids():
    plan = AssemblyPlan(
        name="Duplicate IDs",
        instructions=[
            AssemblyInstruction("base", "brick_4x2"),
            AssemblyInstruction("base", "brick_2x2"),
        ],
    )

    with pytest.raises(ValueError, match="Duplicate component ID"):
        validate_assembly_plan(plan)

def test_parent_component_does_not():
    plan = AssemblyPlan(
        name="Missing Parent",
        instructions=[
            AssemblyInstruction(
                component_id="body",
                component_type="brick_2x2",
                parent_id="unknown",
                attachment="top",
            ),
        ]
    )

    with pytest.raises(ValueError, match="does not exist"):
        validate_assembly_plan(plan)

def test_component_not_its_own_parent():
    plan = AssemblyPlan(
        name="Self Parent",
        instructions=[
            AssemblyInstruction(
                component_id="body",
                component_type="brick_2x2",
                parent_id="body",
                attachment="top",
            )
        ],
    )

    with pytest.raises(ValueError, match="own parent"):
        validate_assembly_plan(plan)

