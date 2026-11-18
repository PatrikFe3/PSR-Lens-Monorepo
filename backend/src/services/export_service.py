from pathlib import Path

from src.config.paths import MODELS_DIR

import cadquery as cq

def export_stl(
        model,
        output_path: Path = MODELS_DIR / "generated_robot.stl",
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cq.exporters.export(
        model,
        str(output_path),
    )