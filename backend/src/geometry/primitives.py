import cadquery as cq

def create_box(
        length: float = 1.0,
        width: float = 1.0,
        height: float = 1.0,
) -> cq.Workplane:
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError("length and width and height must be positive.")

    return (
        cq.Workplane("XY")
        .box(length, width, height)
    )


def create_cylinder(
        radius: float = 1.0,
        height: float = 1.0,
) -> cq.Workplane:
    if radius <= 0 or height <= 0:
        raise ValueError("radius and height must be positive.")

    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
    )

def create_sphere(
        radius: float = 1.0,
) -> cq.Workplane:
    if radius <= 0:
        raise ValueError("radius must be positive.")
    return (
        cq.Workplane("XY")
        .sphere(radius)
    )

def create_torus(
        major_radius: float,
        minor_radius: float,
) -> cq.Workplane:

    if major_radius <= 0 or minor_radius <= 0:
        raise ValueError("major_radius and minor_radius must be positive.")

    if minor_radius >= major_radius:
        raise ValueError("minor_radius must not be greater than major_radius.")

    torus = cq.Solid.makeTorus(
        major_radius,
        minor_radius,
        pnt=cq.Vector(0, 0, 0),
        dir=cq.Vector(0, 0, 1)
    )

    return cq.Workplane("XY").newObject([torus])

def create_pipe (
        outer_radius: float,
        inner_radius: float,
        length: float,
) -> cq.Workplane:

    if outer_radius <= 0 or inner_radius <= 0 or length <= 0:
        raise ValueError("outer_radius and inner_radius must be positive.")

    if inner_radius >= outer_radius:
        raise ValueError("inner_radius must not be greater than outer_radius.")

    return (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length)
    )

def create_coil(
        radius: float,
        height: float,
        pitch: float,
        wire_radius: float,
) -> cq.Workplane:

    if radius <= 0 or height <= 0:
        raise ValueError("Coil radius and height must be positive.")

    if pitch <= 0 or wire_radius <= 0:
        raise ValueError("Pitch and wire radius must be positive.")

    if pitch > height:
        raise ValueError("Pitch cannot be greater than coil height.")

    path = cq.Wire.makeHelix(
        pitch=pitch,
        height=height,
        radius=radius,
    )

    start_point = path.Vertices()[0].Center()

    profile = (
        cq.Workplane("XZ")
        .workplane(offset=start_point.z)
        .center(start_point.x, start_point.y)
        .circle(wire_radius)
    )

    return profile.sweep(
        path,
        isFrenet=True,
    )


