import cadquery as cq

from src.assembly.assembly_component import AssemblyComponent
from src.data_models.assembly_result import AssemblyResult
from src.collections.brick_collection import BRICK_COLLECTION
from src.geometry.generators.brick_generator import generate_brick
from src.geometry.transformations.translate import translate_model
from src.geometry.transformations.rotate import rotate_model

def generate_assembly(
        components: list[AssemblyComponent],
) -> AssemblyResult:

    placed_models = []

    brick_configs = {
        brick["name"]: brick
        for brick in BRICK_COLLECTION
    }

    for component in components:

        if component.component_type not in brick_configs:
            raise ValueError(
                f"Unknown component type: {component.component_type}"
            )

        config = brick_configs[component.component_type]

        parameters = {
            key: value
            for key, value in config.items()
            if key != "name"
        }

        model = generate_brick(**parameters)

        if component.rotation != 0:
            model = rotate_model(
                model=model,
                axis_start=(0,0,0),
                axis_end=(0,0,1),
                angle=component.rotation,
            )

        model = translate_model(
            model=model,
            x=component.x,
            y=component.y,
            z=component.z,
        )

        placed_models.append(model.val())

    if not placed_models:
        raise ValueError("Assembly must contain at least one component.")

    assembly_model = cq.Compound.makeCompound(placed_models)

    return AssemblyResult(
        model=assembly_model,
        components=components,
    )