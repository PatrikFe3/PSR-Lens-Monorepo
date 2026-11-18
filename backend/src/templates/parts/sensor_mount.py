"""An L-shaped bracket that holds a small board (e.g. a camera) upright, facing -Y."""
import numpy as np

from src.core.frames import Frame, rot_x, translate
from src.geometry.kernel import kernel
from src.templates.base import (ALL_INTERFACES, Auto, Body, BuildContext, BuiltPart, Site, Template,
                                TemplateParams, auto)
from src.templates.features.standoffs import standoff_radius

# Board frame -> part frame: board X stays X, board Y points up (+Z), board Z (the
# side with the lens) points forward (-Y).
_UPRIGHT = np.array([[1.0, 0.0, 0.0, 0.0],
                     [0.0, 0.0, -1.0, 0.0],
                     [0.0, 1.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0, 1.0]])


class SensorMountParams(TemplateParams):
    hardware: str
    wall: float | Auto = 'auto'
    margin: float | Auto = 'auto'      # border around the board on the upright plate


class SensorMount(Template):
    name = 'sensor_mount'
    description = ('L-bracket holding a small board (camera, sensor) upright and facing forward (-Y). '
                   'Site "base" is under the foot.')
    Params = SensorMountParams
    sites = {'base': ALL_INTERFACES}
    hardware_categories = ('camera', 'sensor', 'board')

    def resolve(self, params, ctx: BuildContext, assembly=None):
        return params.model_copy(update={
            'wall': auto(params.wall, ctx.printer.default_wall),
            'margin': auto(params.margin, 3.0),
        })

    def build(self, part_id, params, ctx):
        k = kernel()
        hw = ctx.hardware[params.hardware]
        b, wall, margin = hw.board, params.wall, params.margin
        standoff_h = hw.mounting.standoff_height if hw.mounting else 1.0
        foot_t = max(2 * wall, 5.0)
        plate_t = 1.5 * wall
        plate_w = b.length + 2 * margin
        board_z = foot_t + margin
        plate_h = board_z + b.width + margin
        foot_front = -(standoff_h + b.thickness + 12.0)

        foot = k.box((plate_w, plate_t - foot_front, foot_t), (0, (plate_t + foot_front) / 2, foot_t / 2))
        plate = k.box((plate_w, plate_t, plate_h), (0, plate_t / 2, plate_h / 2))
        shape = k.fuse(foot, plate)

        board_pose = translate(-b.length / 2, -standoff_h, board_z) @ _UPRIGHT
        if hw.mounting:
            pilot = ctx.pilot_diameter(hw.mounting.screw, hw.mounting.hole_diameter * 0.8)
            r = standoff_radius(pilot)
            for hx, hy in hw.mounting.holes:
                x, z = -b.length / 2 + hx, board_z + hy
                post = k.transform(k.cylinder(r, standoff_h + 0.5), translate(x, 0.5, z) @ rot_x(90))
                hole = k.transform(k.cylinder(pilot / 2, standoff_h + 1.7), translate(x, 1.5, z) @ rot_x(90))
                shape = k.cut(k.fuse(shape, post), hole)

        site_y = (plate_t + foot_front) / 2
        sites = {'base': Site('base', Frame((0, site_y, 0), (0, 0, -1)), self.sites['base'])}
        return BuiltPart(part_id, self.name, params, {'main': Body(shape, '-Z')}, sites,
                         holds=[(params.hardware, np.array(board_pose))])
