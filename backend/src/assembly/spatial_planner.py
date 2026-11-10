from src.data_models.assembly_plan import AssemblyPlan
from src.assembly.assembly_component import AssemblyComponent
from src.collections.brick_collection import BRICK_COLLECTION

def plan_spatial_layout(
        plan: AssemblyPlan,
) -> list[AssemblyComponent]:

    brick_configs = {
        brick["name"]: brick
        for brick in BRICK_COLLECTION
    }

    components = []
    placed_by_id = {}
    pending = list(plan.instructions)

    while pending:

        progress = False

        for instruction in pending[:]:

            if instruction.component_type not in brick_configs:
                raise ValueError(
                    f"Unknown component type: {instruction.component_type}"
                )

            config = brick_configs[instruction.component_type]

            if instruction.parent_id is None:

                component = AssemblyComponent(
                    component_type=instruction.component_type,
                    x=0,
                    y=0,
                    z=0,
                )

            elif instruction.parent_id in placed_by_id:

                if instruction.attachment != "top":
                    raise ValueError(
                        f"Unsupported attachment: {instruction.attachment}"
                    )

                parent_component, parent_config = placed_by_id[instruction.parent_id]

                parent_height = parent_config.get("base_height", 5.0)
                child_height = config.get("base_height", 5.0)

                component = AssemblyComponent(
                    component_type=instruction.component_type,
                    x=parent_component.x,
                    y=parent_component.y,
                    z=(
                        parent_component.z
                        + parent_height / 2
                        + child_height / 2
                    ),
                )
            else:

                continue

            components.append(component)

            placed_by_id[instruction.component_id] = (
                component,
                config,
            )

            pending.remove(instruction)
            progress = True

        if not progress:
            raise ValueError(
                "Unable to resolve component positions."
                "Check parent relationships in AssemblyPlan"
            )

    return components
