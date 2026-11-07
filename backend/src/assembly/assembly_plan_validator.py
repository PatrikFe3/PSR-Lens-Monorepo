from src.data_models.assembly_plan import AssemblyPlan

def validate_assembly_plan(plan: AssemblyPlan) -> None:
    if not plan.instructions:
        raise ValueError("Assembly plan cannot be empty.")

    component_ids = set()

    for instruction in plan.instructions:

        if not instruction.component_id:
            raise ValueError(f"Duplicate component ID: {instruction.component_id}")

        component_ids.add(instruction.component_id)

    for instruction in plan.instructions:

        if instruction.parent_id is None:
            if instruction.attachment is not None:
                raise ValueError(f"Root component cannot have an attachment.")
            continue

        if instruction.parent_id not in component_ids:
            raise ValueError(f"Parent component {instruction.parent_id} does not exist.")

        if instruction.parent_id == instruction.component_id:
            raise ValueError("Component cannot be its own parent.")

        if not instruction.attachment:
            raise ValueError(f"Component {instruction.component_id} must define an attachment.")

        parents = {
            instruction.component_id: instruction.parent_id
            for instruction in plan.instructions
        }

        for component_id in component_ids:

            visited = set()

            current_id = component_id

            while current_id is not None:

                if current_id in visited:
                    raise ValueError(f"Circular parent relationship detected at '{current_id}'.")

                visited.add(current_id)
                current_id = parents[current_id]