from src.data_models.component_position import ComponentPosition
from src.validators.assembly_plan_validator import validate_assembly_plan
from src.data_models.assembly_plan import AssemblyPlan
from src.assembly.assembly_component import AssemblyComponent
from src.collections.brick_collection import BRICK_COLLECTION
from src.data_models.component_dimensions import ComponentDimensions


def get_component_dimensions(
        config: dict,
) -> ComponentDimensions:
    stud_spacing = config.get("stud_spacing", 8.0)

    length = config["studs_x"] * stud_spacing
    width = config["studs_y"] * stud_spacing
    height = config.get("base_height", 5.0)

    return ComponentDimensions(
        length=length,
        width=width,
        height=height,
    )

def plan_spatial_layout(
        plan: AssemblyPlan,
) -> list[AssemblyComponent]:

    validate_assembly_plan(plan)

    brick_configs = {
        brick["name"]: brick
        for brick in BRICK_COLLECTION
    }

    components = []
    placed_by_id = {}
    pending = list(plan.instructions)


    while pending:

        progress = False
        instruction_to_process = list(pending)

        for instruction in instruction_to_process:

            if instruction.component_type not in brick_configs:
                raise ValueError(
                    f"Unknown component type: {instruction.component_type}"
                )

            config = brick_configs[instruction.component_type]

            if instruction.parent_id is None:

                dimensions = get_component_dimensions(config)

                position = ComponentPosition(
                    x=0.0,
                    y=0.0,
                    z=dimensions.height / 2,
                )

            elif instruction.parent_id in placed_by_id:

                parent_component, parent_config = (
                    placed_by_id[instruction.parent_id]
                )

                position = calculate_child_position(
                    parent_component=parent_component,
                    parent_config=parent_config,
                    child_config=config,
                    attachment=instruction.attachment,
                )

            else:
                continue

            component = AssemblyComponent(
                component_type=instruction.component_type,
                x=position.x,
                y=position.y,
                z=position.z,
            )

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

def calculate_child_position(
        parent_component: AssemblyComponent,
        parent_config: dict,
        child_config: dict,
        attachment: str,
) -> ComponentPosition:

    parent_dimensions = get_component_dimensions(parent_config)
    child_dimensions = get_component_dimensions(child_config)

    x = parent_component.x
    y = parent_component.y
    z = parent_component.z

    if attachment == "top":
        z += (parent_dimensions.height / 2 + child_dimensions.height / 2)

    elif attachment == "bottom":
        z -= (parent_dimensions.height / 2 + child_dimensions.height / 2)

    elif attachment == "right":
        x += (parent_dimensions.length / 2 + child_dimensions.length / 2)

    elif attachment == "left":
        x -= (parent_dimensions.length / 2 + child_dimensions.length / 2)

    elif attachment == "front":
        y += (parent_dimensions.width / 2 + child_dimensions.width / 2)

    elif attachment == "back":
        y -= (parent_dimensions.width / 2 + child_dimensions.width / 2)

    else:
        raise ValueError(
            f"Unsupported attachment: {attachment}"
        )
    return ComponentPosition(
        x=x,
        y=y,
        z=z,
    )

