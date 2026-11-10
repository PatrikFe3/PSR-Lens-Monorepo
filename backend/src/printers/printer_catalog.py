from src.printers.printer_profile import PrinterProfile

ENDER_6 = PrinterProfile(
    name="Creality Ender 6",
    build_volume_x=250.0,
    build_volume_y=250.0,
    build_volume_z=400.0,
    technology="FDM",
    filament_diameter=1.75,
    nozzle_diameter=0.4,
    max_nozzle_temperature=None,
    max_bed_temperature=None,
    supported_materials=("PLA",),
)

MK_4_S = PrinterProfile(
    name="Prusa MK 4 S",
    build_volume_x=250.0,
    build_volume_y=210.0,
    build_volume_z=220.0,
    technology="FDM",
    filament_diameter=1.75,
    nozzle_diameter=0.4,
    max_nozzle_temperature=None,
    max_bed_temperature=None,
    supported_materials=("PLA",),
)

ORIGINAL_MINI_PLUS = PrinterProfile(
    name="Prusa MINI+",
    build_volume_x=180.0,
    build_volume_y=180.0,
    build_volume_z=180.0,
    technology="FDM",
    filament_diameter=1.75,
    nozzle_diameter=0.4,
    max_nozzle_temperature=None,
    max_bed_temperature=None,
    supported_materials=("PLA",),
)