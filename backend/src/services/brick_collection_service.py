import cadquery as cq

from pathlib import Path

from src.config.paths import MODELS_DIR
from src.geometry.generators.brick_generator import generate_brick
from src.collections.brick_collection import BRICK_COLLECTION

def generate_brick_collection(
        output_dir: Path = MODELS_DIR,
) -> list[Path]:

    output_dir.mkdir(exist_ok=True, parents=True)

    generated_files = []

    for brick_config in BRICK_COLLECTION:
        name = brick_config["name"]

        parameters = {
            key: value
            for key, value in brick_config.items()
            if key != "name"
        }

        print(f"Generating: {name}")

        model = generate_brick(**parameters) #The usage of ** is to unwrap the dictionary from named argument functions

        output_path = output_dir / f"{name}.stl"

        cq.exporters.export(
            model,
            str(output_path),
            exportType="STL",
        )

        generated_files.append(output_path)

        print(f"Saved: {output_path}")

    return generated_files