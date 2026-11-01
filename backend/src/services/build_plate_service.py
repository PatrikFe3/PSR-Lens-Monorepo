from pathlib import Path

import cadquery as cq
from trame_vtk.modules.vtk.widget import value

from src.config.paths import MODELS_DIR
from src.collections.brick_collection import BRICK_COLLECTION
from src.geometry.generators.brick_generator import generate_brick
from src.geometry.transformations.rotate import rotate_model
from src.geometry.transformations.translate import translate_model

from src.algorithms.layout_optimizer import (
    ModelDimensions,
    optimize_layout,
)

def generate_build_plate(
        plate_width: float,
        plate_depth: float,
        spacing: float= 3.0,
        output_path: Path = MODELS_DIR / "build_plate.stl",
) -> Path:

    models = {}
    dimensions = []

    for config in BRICK_COLLECTION:

        name = config["name"]

        parameters = {
            key: value
            for key, value in config.items()
            if key != "name"
        }

        model = generate_brick(**parameters)

        bounding_box = model.val().BoundingBox()

        models[name] = model

        dimensions.append(
            ModelDimensions(
                name=name,
                width=bounding_box.xlen,
                depth=bounding_box.ylen,
            )
        )

    placements = optimize_layout(
        models=dimensions,
        plate_width=plate_width,
        plate_depth=plate_depth,
        spacing=spacing,
    )

    placed_models = []

    for placement in placements:

        model = models[placement.name]

        if placement.rotation == 90:
            model = rotate_model(
                model=model,
                axis_start=(0,0,0),
                axis_end=(0,0,1),
                angle=90,
            )

        bounding_box = model.val().BoundingBox()

        model = translate_model(
            model=model,
            x=placement.x - bounding_box.xmin,
            y=placement.y - bounding_box.ymin,
            z=-bounding_box.zmin,
        )

        placed_models.append(model.val())

        print(
            f"{placement.name}: "
            f"X={placement.x:.2f}, "
            f"Y={placement.y:.2f}, "
            f"Rotation={placement.rotation}°"
        )

        compound = cq.Compound.makeCompound(placed_models)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cq.exporters.export(
            compound,
            str(output_path),
            exportType="STL",
        )

        print(f"\nBuild plate exported: {output_path}")

        return output_path