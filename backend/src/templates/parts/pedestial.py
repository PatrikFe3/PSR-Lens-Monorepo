"""
    A heavy round base-plate - the usual root of a turret or arm.
"""
from src.core.frames import Frame
from src.geometry.kernel import kernel
from src.templates.base import (ALL_INTERFACES, Auto, Body, BuildContext, BuiltPart, Site, Template,
                                TemplateParams, auto)


class PedestalParams(TemplateParams):
    diameter: float | Auto = 'auto'
    height: float | Auto = 'auto'


class Pedestal(Template):
    name = 'pedestal'
    description = 'Solid round base plate (default 90 mm across, 12 mm tall). Sites on top and bottom.'
    Params = PedestalParams
    sites = {'top': ALL_INTERFACES, 'bottom': ALL_INTERFACES}

    def resolve(self, params, ctx: BuildContext, assembly=None):
        return params.model_copy(update={
            'diameter': auto(params.diameter, 90.0),
            'height': auto(params.height, 12.0),
        })

    def build(self, part_id, params, ctx):
        k = kernel()
        d, h = params.diameter, params.height
        shape = k.cylinder(d / 2, h)
        sites = {
            'top': Site('top', Frame((0, 0, h), (0, 0, 1)), self.sites['top']),
            'bottom': Site('bottom', Frame((0, 0, 0), (0, 0, -1)), self.sites['bottom']),
        }
        return BuiltPart(part_id, self.name, params, {'main': Body(shape, '-Z')}, sites)
