"""A LEGO-sized block. Join bricks with the ``stud_grid`` interface."""
from src.core.frames import Frame
from src.geometry.kernel import kernel
from src.templates.base import Auto, Body, BuildContext, BuiltPart, Site, Template, TemplateParams, auto

_PITCH = 8.0
_BRICK_SITES = ('stud_grid', 'screw_m2_5', 'dovetail', 'revolute_pin')


class BrickParams(TemplateParams):
    studs_x: int = 2
    studs_y: int = 2
    height: float | Auto = 'auto'


class Brick(Template):
    name = 'brick'
    description = 'Solid block sized like a LEGO brick (8 mm pitch, 9.6 mm tall). Sites on top and bottom.'
    Params = BrickParams
    sites = {'top': _BRICK_SITES, 'bottom': _BRICK_SITES}

    def resolve(self, params, ctx: BuildContext, assembly=None):
        if params.studs_x < 1 or params.studs_y < 1:
            raise ValueError('A brick needs at least 1 x 1 studs.')
        return params.model_copy(update={'height': auto(params.height, 9.6)})

    def build(self, part_id, params, ctx):
        k = kernel()
        lx, ly, h = params.studs_x * _PITCH - 0.2, params.studs_y * _PITCH - 0.2, params.height
        shape = k.box((lx, ly, h), (0, 0, h / 2))
        sites = {
            'top': Site('top', Frame((0, 0, h), (0, 0, 1)), self.sites['top']),
            'bottom': Site('bottom', Frame((0, 0, 0), (0, 0, -1)), self.sites['bottom']),
        }
        return BuiltPart(part_id, self.name, params, {'main': Body(shape, '-Z')}, sites)
