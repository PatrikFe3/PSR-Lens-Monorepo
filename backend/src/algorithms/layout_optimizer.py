#2D Rectangle Packing

from dataclasses import dataclass

@dataclass
class ModelPlacement:
    name: str
    x: float
    y: float
    width: float
    depth: float
    rotation: int

@dataclass
class ModelDimensions:
    name: str
    width: float
    depth: float

def optimize_layout(
        models: list[ModelDimensions],
        plate_width: float,
        plate_depth: float,
        spacing: float = 3.0,
) -> list[ModelPlacement]:
    if plate_width <= 0 or plate_depth <= 0:
        raise ValueError("Build plate dimensions must be positive.")

    if spacing < 0:
        raise ValueError("Spacing cannot be negative.")

    placements = []

    sorted_models = sorted(
        models,
        key=lambda model: model.width * model.depth,
        reverse=True,
    )

    for model in sorted_models:

        if model.width <= 0 or model.depth <= 0:
            raise ValueError(f"Invalid dimensions for {model.name}")

        candidate_x = {0.0}
        candidate_y = {0.0}

        for placed in placements:
            candidate_x.add(placed.x + placed.width + spacing)
            candidate_y.add(placed.y + placed.depth + spacing)

        candidates = sorted(
            (
                (x, y)
                for y in candidate_y
                for x in candidate_x
            ),
            key=lambda position: (position[1], position[0]),
        )

        selected = None

        for rotation in (0, 90):

            if rotation == 0:
                width = model.width
                depth = model.depth
            else:
                width = model.depth
                depth = model.width

            if width > plate_width or depth > plate_depth:
                continue

            for x, y in candidates:

                if x + width > plate_width:
                    continue

                if y + depth > plate_depth:
                    continue

                overlaps = any(
                    x < placed.x + placed.width + spacing
                    and x + width + spacing > placed.x
                    and y < placed.y + placed.depth + spacing
                    and y + depth + spacing > placed.y
                    for placed in placements
                )

                if not overlaps:
                    selected = ModelPlacement(
                        name=model.name,
                        x=x,
                        y=y,
                        width=width,
                        depth=depth,
                        rotation=rotation,
                    )
                    break

            if selected is not None:
                break

        if selected is None:
            raise ValueError(
                f"Model '{model.name}' cannot fit on the build plate."
            )

        placements.append(selected)

    return placements