from dataclasses import dataclass

@dataclass
class PrinterProfile:
    name: str
    build_volume_x: float
    build_volume_y: float
    build_volume_z: float
    technology: str = "FDM"
    filament_diameter: float=1.75
    nozzle_diameter: float=1.75

    max_nozzle_temperature: float| None = None
    max_bed_temperature: float| None = None

    supported_materials: tuple[str, ...] = ()

def validate_model_fits(
        length: float,
        width: float,
        height: float,
        printer: PrinterProfile,
        margin: float = 5.0,
) -> None:
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError("Model dimensions must be positive.")

    if margin < 0:
        raise ValueError("Margin cannot be negative.")

    if length + margin > printer.build_volume_x:
        raise ValueError("Model is too long for the printer.")

    if width + margin > printer.build_volume_y:
        raise ValueError("Model is too wide for the printer.")

    if height + margin > printer.build_volume_z:
        raise ValueError("Model is too tall for the printer.")