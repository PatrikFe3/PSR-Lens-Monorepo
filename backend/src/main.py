import cadquery as cq
from src.config.paths import MODELS_DIR
from src.geometry.generators.beam_generator import generate_beam
from src.printers.printer_profile import (
    PrinterProfile,
    validate_model_fits,
)

from src.assembly.assembly_plan_validator import validate_assembly_plan
from src.data_models.assembly_plan import (
    AssemblyPlan,
    AssemblyInstruction,
)

from src.assembly.spatial_planner import plan_spatial_layout

from src.geometry.model_builder import ModelBuilder
from src.services.brick_collection_service import generate_brick_collection
from src.services.build_plate_service import generate_build_plate

from src.services.assembly_service import generate_assembly


def main() -> None:

    robot_plan = AssemblyPlan(
        name="Simple Robot",
        instructions=[
            AssemblyInstruction(
                component_id="base",
                component_type="brick_6x2"
            ),
            AssemblyInstruction(
                component_id="body",
                component_type="brick_2x2",
                parent_id="base",
                attachment="top"
            ),
            AssemblyInstruction(
                component_id="head",
                component_type="brick_6x2",
                parent_id="body",
                attachment="top"
            ),
            AssemblyInstruction(
                component_id="hair",
                component_type="brick_4x2",
                parent_id="head",
                attachment="top"
            )
        ]
    )

    validate_assembly_plan(robot_plan)

    print("Assembly plan is valid!")

    components = plan_spatial_layout(robot_plan)

    generated_files = generate_brick_collection()

    assembly_result = generate_assembly(components)

    assembly_path = MODELS_DIR / "assembly.stl"

    cq.exporters.export(
        assembly_result.model,
        str(assembly_path),
        exportType="STL",
    )

    print(f"Assembly exported: {assembly_path.resolve()}")

    generate_build_plate(
        components=assembly_result.components,
        plate_width=250,
        plate_depth=250,
        spacing=3.0,
    )

    print("\nCollection generation completed!")
    print(f"Generated {len(generated_files)} models.")

    printer = PrinterProfile(
        name="Creality Ender 6",
        build_volume_x=250.0,
        build_volume_y=250.0,
        build_volume_z=400.0,
    )

    print(f"=== 3D Model generator:{printer.name}===")
    print("1. Beam")
    print("2. Ribbed cylinder")

    choice = input("Choose model type: ").strip()

    try:
        if choice == "1":
            length = get_positive_number("Enter the length of the model (mm): ")
            width = get_positive_number("Enter the width of the model (mm): ")
            height = get_positive_number("Enter the height of the model (mm): ")

            validate_model_fits(
                length = length,
                width = width,
                height = height,
                printer = printer,
            )

            generate_beam(
                length=length,
                width=width,
                height=height,
            )

        elif choice == "2":
            radius = get_positive_number("Enter the radius of the model (mm): ")
            height = get_positive_number("Enter the height of the model (mm): ")

            validate_model_fits(
                length=2 * (radius + 2.0),
                width=2 * (radius + 2.0),
                height=height,
                printer = printer,
            )

            bevel_choice = input("Choose bevel model (none / fillet / chamfer): ").strip().lower()
            rib_choice = input("Choose rib type (straight / twisted): ").strip().lower()

            if rib_choice == "twisted":
                if bevel_choice not in ("none", "fillet", "chamfer"):
                    raise ValueError("Unknown edge treatment.")
            bevel_size = None

            if bevel_choice != "none":
                bevel_size = get_positive_number("Enter the size of the bevel model (mm): ")

            taper_choice = input("Apply taper deformation? (yes / no):").strip().lower()
            if taper_choice not in ("yes", "no"):
                raise ValueError("Choose yes or no.")

            taper_amount = 0.0

            if taper_choice == "yes":
                taper_percent = get_positive_number("Enter the percentage of the taper (%): ")
                if taper_percent >= 100:
                    raise ValueError("Taper must be less than 100%.")

                taper_amount = taper_percent / 100.0

            ModelBuilder.build_ribbed_cylinder(
                radius=radius,
                height=height,
                rib_count=12,
                bevel_type=bevel_choice,
                bevel_size=bevel_size,
                taper_amount=taper_amount,
            )

        else:
            print("Invalid model selection.")

    except ValueError as error:
        print(f"Cannot generate model:{error}")
        return


def get_positive_number(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))

            if value <= 0:
                print("The value must be greater then zero.")
                continue

            return value
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
