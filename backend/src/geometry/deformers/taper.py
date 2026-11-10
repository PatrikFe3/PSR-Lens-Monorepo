import cadquery as cq
import trimesh

def apply_taper_deformer(
        model: cq.Workplane,
        amount: float,
        tolerance: float= 0.1,
        angular_tolerance: float= 0.1,
) -> trimesh.Trimesh:
    if not 0 <= amount <= 1:
        raise ValueError("Taper amount must be between 0 and 1.")

    if tolerance <= 0 or angular_tolerance <= 0:
        raise ValueError("Tesselation tolerance must be positive.")

    shape = model.val()

    vertices, triangles, = shape.tessellate(
        tolerance,
        angular_tolerance,
    )

    if not vertices or not triangles:
        raise ValueError("Could not create a mesh from the model.")

    mesh = trimesh.Trimesh(
        vertices=[
            (vertex.x, vertex.y, vertex.z) for vertex in vertices
        ],
        faces=triangles,
        process=True,
    )

    z_min = float(mesh.bounds[0][2])
    z_max = float(mesh.bounds[1][2])
    height = z_max - z_min

    if height <= 0:
        raise ValueError("Model must have a positive height.")

    relative_height = (
        mesh.vertices[:, 2] - z_min
    ) / height

    scale = 1.0 - amount * relative_height

    mesh.vertices[:, 0] *= scale
    mesh.vertices[:, 1] *= scale

    mesh.fix_normals()

    return mesh