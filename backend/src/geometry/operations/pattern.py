import cadquery as cq

def surface_array(
        model: cq.Workplane,
        count_x: int,
        count_y: int,
        spacing_x: float,
        spacing_y: float,
        centered: bool = True,
) -> cq.Workplane:

    if model is None:
        raise ValueError("Model cannot be None.")

    if count_x < 1 or count_y < 1:
        raise ValueError("Counts must be at least 1.")

    if spacing_x <= 0 or spacing_y <= 0:
        raise ValueError("Spacing must be greater than 0.")

    source = model.val()

    if source is None:
        raise ValueError("Model contains no geometry.")

    copies = []

    for index_x in range (count_x):
        for index_y in range (count_y):

            if centered:
                x = (index_x - (count_x - 1) / 2) * spacing_x
                y = (index_y - (count_y - 1) / 2) * spacing_y
            else:
                x = index_x * spacing_x
                y = index_y * spacing_y

            copies.append(source.translate((x, y, 0)))

    compound = cq.Compound.makeCompound(copies)

    return cq.Workplane("XY").newObject([compound])

def linear_array(
        model: cq.Workplane,
        count: int,
        spacing: float,
        direction: str = "X",
        centered: bool = False,
) -> cq.Workplane:

    if model is None:
        raise ValueError("Model must be provided")

    if count < 1:
        raise ValueError("Count must be at least 1")

    if spacing <= 0:
        raise ValueError("Spacing must be positive")

    if direction not in ["X", "Y", "Z"]:
        raise ValueError("Direction must be X or Y, or Z")

    source = model.val()

    if source is None:
        raise ValueError("Model contains no geometry")

    copies = []

    for i in range (count):

        if centered:
            offset = (i - (count - 1)) / 2 * spacing
        else:
            offset = i * spacing

        x = offset if direction == "X" else 0
        y = offset if direction == "Y" else 0
        z = offset if direction == "Z" else 0

        copies.append(source.translate((x, y, z)))

    compound = cq.Compound.makeCompound(copies)

    return cq.Workplane("XY").newObject([compound])

def radial_array(
        model: cq.Workplane,
        count: int,
        spacing: float,
        axis_start: tuple = (0, 0, 0),
        axis_end: tuple = (0, 0, 1),
        total_angle: float = 360.0,
) -> cq.Workplane:

    if model is None:
        raise ValueError("Model must be provided")

    if count < 1:
        raise ValueError("Count must be at least 1")

    if spacing < 1:
        raise ValueError("Spacing must be at least 1")

    if total_angle <= 0 or total_angle > 360:
        raise ValueError("Total angle must be between 0 and 360.")

    source = model.val()

    if source is None:
        raise ValueError("Model contains no geometry.")

    copies = []
    angle_step = total_angle / count

    for i in range (count):
        angle = i * angle_step

        copy = source.rotate(
            axis_start,
            axis_end,
            angle,
        )

        copies.append(copy)

    compound = cq.Compound.makeCompound(copies)

    return cq.Workplane("XY").newObject([compound])