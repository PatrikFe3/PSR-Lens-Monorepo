from src.data_models.assembly_plan import AssemblyPlan

ATTACHMENTS = ("top", "bottom", "left", "right", "front", "back")


def validate_assembly_plan(
        plan: AssemblyPlan,
) -> None:

    if not plan.instructions:
        raise ValueError(
            "Assembly plan cannot be empty: it must contain at least one component."
        )

    for instruction in plan.instructions:
        if not instruction.component_id or not instruction.component_id.strip():
            raise ValueError("Component ID cannot be empty.")

    component_ids = [
        instruction.component_id
        for instruction in plan.instructions
    ]

    duplicates = sorted({cid for cid in component_ids if component_ids.count(cid) > 1})
    if duplicates:
        raise ValueError(
            f"Duplicate component ID: {', '.join(duplicates)}. Every component must have a unique component_id."
        )

    instructions_by_id = {
        instruction.component_id: instruction
        for instruction in plan.instructions
    }

    # Per-component checks first, so the most specific error is reported.
    for instruction in plan.instructions:

        if instruction.parent_id is None:
            continue

        if instruction.parent_id == instruction.component_id:
            raise ValueError(
                f"Component {instruction.component_id} cannot be its own parent."
            )

        if instruction.parent_id not in instructions_by_id:
            raise ValueError(
                f"Parent component '{instruction.parent_id}' of '{instruction.component_id}' does not exist."
            )

        if instruction.attachment not in ATTACHMENTS:
            raise ValueError(
                f"Unsupported attachment '{instruction.attachment}' for component '{instruction.component_id}'."
            )

    root_components = [
        instruction
        for instruction in plan.instructions
        if instruction.parent_id is None
    ]

    if len(root_components) != 1:
        raise ValueError(
            "Assembly plan must contain exactly one root component."
        )

    root = root_components[0]

    if root.attachment is not None:
        raise ValueError(
            "Root component must have attachment=None."
        )

    for instruction in plan.instructions:

        visited_ids = set()
        current_instruction = instruction

        while current_instruction.parent_id is not None:

            if current_instruction.component_id in visited_ids:
                raise ValueError("Circular parent relationship detected.")

            visited_ids.add(current_instruction.component_id)

            current_instruction = instructions_by_id[current_instruction.parent_id]

        if current_instruction.component_id != root.component_id:
            raise ValueError(f"Component '{instruction.component_id}' is not connected to the root component.")
