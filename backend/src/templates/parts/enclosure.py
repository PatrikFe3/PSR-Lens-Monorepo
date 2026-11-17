"""A two-piece box (tray + lid) sized automatically around one circuit board."""
import numpy as np

from src.core.frames import Frame, translate
from src.geometry.kernel import kernel
from src.templates.base import (ALL_INTERFACES, Auto, Body, BuildContext, BuiltPart, Site, Template,
                                TemplateParams, auto)
from src.templates.features.cutouts import lid_slots, port_cutouts
from src.templates.features.shell import lid, open_tray
from src.templates.features.standoffs import standoffs
from src.templates.features.vents import vent_slots

LIP_HEIGHT = 2.0


class EnclosureParams(TemplateParams):
    hardware: str                      # id of an entry in the spec's "hardware" list
    wall: float | Auto = 'auto'
    clearance: float | Auto = 'auto'   # free space around the board
    vents: bool = True


class Enclosure(Template):
    name = 'enclosure'
    description = ('Tray and lid that fit one board from the hardware list (holes for its ports, '
                   'standoffs, vents over hot chips). Sites: "top" (on the lid) and "bottom".')
    Params = EnclosureParams
    sites = {'top': ALL_INTERFACES, 'bottom': ALL_INTERFACES}
    hardware_categories = ('sbc', 'sensor', 'board', 'display', 'camera')

    def resolve(self, params, ctx: BuildContext, assembly=None):
        return params.model_copy(update={
            'wall': auto(params.wall, ctx.printer.default_wall),
            'clearance': auto(params.clearance, 1.0),
        })

    @staticmethod
    def dimensions(hw, wall: float, clr: float) -> dict:
        b, env = hw.board, hw.envelope
        standoff = max(hw.mounting.standoff_height if hw.mounting else 0.0, env.below + 0.5)
        inner_l, inner_w = b.length + 2 * clr, b.width + 2 * clr
        board_z = wall + standoff
        height = board_z + b.thickness + env.above + clr + LIP_HEIGHT
        return {
            'inner_l': inner_l, 'inner_w': inner_w,
            'outer_l': inner_l + 2 * wall, 'outer_w': inner_w + 2 * wall,
            'standoff': standoff, 'board_z': board_z, 'height': height,
            'board_x0': -b.length / 2, 'board_y0': -b.width / 2,
        }

    def build(self, part_id, params, ctx):
        k = kernel()
        hw = ctx.hardware[params.hardware]
        wall, clr = params.wall, params.clearance
        d = self.dimensions(hw, wall, clr)
        x0, y0, board_z, height = d['board_x0'], d['board_y0'], d['board_z'], d['height']
        board_pose = translate(x0, y0, board_z)

        # tray: shell + standoffs - port openings
        tray = open_tray(d['outer_l'], d['outer_w'], height, wall, wall)
        if hw.mounting:
            pilot = ctx.pilot_diameter(hw.mounting.screw, hw.mounting.hole_diameter * 0.8)
            posts, holes = standoffs(hw.mounting.holes, d['standoff'], pilot, board_pose)
            tray = k.cut(k.fuse(tray, posts), holes)
        ports = port_cutouts(hw, x0, y0, board_z + hw.board.thickness, d['inner_l'], d['inner_w'], wall)
        if ports is not None:
            tray = k.cut(tray, ports)

        # lid: plate + lip - cable slots - vents
        fit = ctx.clearance('sliding')
        top = lid(d['outer_l'], d['outer_w'], wall, height,
                  d['inner_l'] - 2 * fit, d['inner_w'] - 2 * fit, LIP_HEIGHT)
        slots = lid_slots(hw, x0, y0, height, wall)
        if slots is not None:
            top = k.cut(top, slots)
        if params.vents and hw.heat_sources:
            vents = vent_slots([(x0 + h.position[0], y0 + h.position[1]) for h in hw.heat_sources],
                               height, wall)
            top = k.cut(top, vents)

        sites = {
            'top': Site('top', Frame((0, 0, height + wall), (0, 0, 1)), self.sites['top'], body='lid'),
            'bottom': Site('bottom', Frame((0, 0, 0), (0, 0, -1)), self.sites['bottom'], body='main'),
        }
        bodies = {'main': Body(tray, '-Z'), 'lid': Body(top, '+Z')}
        return BuiltPart(part_id, self.name, params, bodies, sites,
                         holds=[(params.hardware, np.array(board_pose))])
