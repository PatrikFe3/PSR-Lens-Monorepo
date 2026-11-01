import cadquery as cq
from typing import Optional
from src.config.paths import MODELS_DIR
from src.geometry.deformers.taper import apply_taper_deformer
from src.geometry.transformations.translate import translate_model
from src.geometry.transformations.rotate import rotate_model
from src.geometry.operations import (
    create_cylinder,
    add_circular_ribs,
    smooth_bevel,
    hard_bevel,
    add_twisted_ribs,
    union_models,
    cut_model,
    intersect_models,
)

class ModelBuilder:

    def __init__(self):
        self._model: Optional[cq.Workplane] = None

    def add(self, model: cq.Workplane) -> "ModelBuilder":
        if self._model is None:
            self._model = model
        else:
            self._model = union_models(
                self._model,
                model,
            )

        return self

    def subtract(self, model: cq.Workplane) -> "ModelBuilder":
        if self._model is None:
            raise ValueError("Cannot subtract from an empty model.")

        self._model = cut_model(
            self._model,
            model,
        )

        return self

    def intersect(self, model: cq.Workplane) -> "ModelBuilder":
        if self._model is None:
            raise ValueError("Cannot intersect from an empty model.")

        self._model = intersect_models(
            self._model,
            model,
        )

        return self

    def build(self) -> cq.Workplane:
        if self._model is None:
            raise ValueError("Cannot build an empty model.")

        return self._model

    def translate(
            self,
            x: float = 0.0,
            y: float = 0.0,
            z: float = 0.0,
    ) -> "ModelBuilder":
        if self._model is None:
            raise ValueError("Cannot translate an empty model.")

        self._model = translate_model(
            model=self._model,
            x=x,
            y=y,
            z=z,
        )
        return self

    def rotate(
            self,
            axis_start: tuple[float, float, float],
            axis_end: tuple[float, float, float],
            angle: float,
    ) -> "ModelBuilder":
        if self._model is None:
            raise ValueError("Cannot rotate an empty model.")

        self._model = rotate_model(
            model=self._model,
            axis_start=axis_start,
            axis_end=axis_end,
            angle=angle,
        )
        
        return self

    @staticmethod
    def build_ribbed_cylinder(
            radius: float,
            height: float,
            rib_count: int,
            rib_type: str = "twisted",
            bevel_type: str = "none",
            bevel_size: float | None = None,
            taper_amount: float = 0.0,
    ) -> None:

        model = create_cylinder(
            radius=radius,
            height=height,
        )
        if rib_type == "straight":
            model = add_circular_ribs(
                model=model,
                radius=radius,
                height=height,
                count=rib_count,
            )
        elif rib_type == "twisted":
            model = add_twisted_ribs(
                model=model,
                radius=radius,
                height=height,
                count=rib_count,
                twist_angle=180.0,
            )
        else:
            raise ValueError(f"Unknown rib type: {rib_type}")

        if bevel_type == "fillet":
            if bevel_size is None or bevel_size <= 0:
                raise ValueError("Fillet radius must be positive.")

            model = smooth_bevel(
                model=model,
                radius=bevel_size,
            )

        elif bevel_type == "chamfer":
            if bevel_size is None or bevel_size <= 0:
                raise ValueError("Chamber radius must be positive.")

            model = hard_bevel(
                model=model,
                distance=bevel_size,
            )

        elif bevel_type != "none":
            raise ValueError(f"Unknown bevel type: {bevel_type}")

        path = MODELS_DIR / "ribbed_cylinder.stl"

        if taper_amount > 0:
            mesh = apply_taper_deformer(
                model=model,
                amount=taper_amount,
            )
            mesh.export(str(path))
        else:
            cq.exporters.export(
                model,
                str(path),
                exportType="STL",)

        print(f"Model saved to {path.resolve()}")


