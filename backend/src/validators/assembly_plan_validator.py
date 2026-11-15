from src.data_models.assembly_plan import AssemblyPlan


def validate_assembly_plan(
        plan: AssemblyPlan,
) -> None:

    if not plan.instructions:
        raise ValueError(
            "Assembly plan must contain at least one component."
        )

    component_ids = [
        instruction.component_id
        for instruction in plan.instructions
    ]

    if len(component_ids) != len(set(component_ids)):
        raise ValueError(
            "Every component must have a unique component_id."
        )

    instructions_by_id = {
        instruction.component_id: instruction
        for instruction in plan.instructions
    }

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

        if instruction is root:
            continue

        if instruction.parent_id == instruction.component_id:
            raise ValueError(
                f"Component {instruction.component_id} cannot be its own parent."
            )

        if instruction.parent_id not in instructions_by_id:
            raise ValueError(
                f"Unknown parent_id: '{instruction.parent_id}' for component '{instruction.component_id}'.'"
            )

        if instruction.attachment not in (
            "top",
            "bottom",
            "left",
            "right",
            "front",
            "back",
        ):
            raise ValueError(
                f"Unsupported attachment '{instruction.attachment}' for component '{instruction.component_id}'."
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
