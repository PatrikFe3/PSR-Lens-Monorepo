"""
    A flat arm with rounded ends: one site underneath one end
    one on top of the other end.
"""
from src.core.frames import Frame
from src.geometry.kernel import kernel
from src.templates.base import (ALL_INTERFACES, Auto, Body, BuildContext, BuiltPart, Site, Template,
                                TemplateParams, auto)


class LinkParams(TemplateParams):
    length: float | Auto = 'auto'      # distance between the two joint centres
    width: float | Auto = 'auto'
    thickness: float | Auto = 'auto'


class Link(Template):
    name = 'link'
    description = ('Flat arm with rounded ends (default 80 mm between joint centres). '
                   'Site "base" is under one end, site "tip" is on top of the other end.')
    Params = LinkParams
    sites = {'base': ALL_INTERFACES, 'tip': ALL_INTERFACES}

    def resolve(self, params, ctx: BuildContext, assembly=None):
        return params.model_copy(update={
            'length': auto(params.length, 80.0),
            'width': auto(params.width, 16.0),
            'thickness': auto(params.thickness, max(8.0, 4 * ctx.printer.default_wall)),
        })

    def build(self, part_id, params, ctx):
        k = kernel()
        length, width, t = params.length, params.width, params.thickness
        bar = k.box((length, width, t), (length / 2, 0, t / 2))
        shape = k.fuse(bar, k.cylinder(width / 2, t, (0, 0, 0)))
        shape = k.fuse(shape, k.cylinder(width / 2, t, (length, 0, 0)))
        sites = {
            'base': Site('base', Frame((0, 0, 0), (0, 0, -1)), self.sites['base']),
            'tip': Site('tip', Frame((length, 0, t), (0, 0, 1)), self.sites['tip']),
        }
        return BuiltPart(part_id, self.name, params, {'main': Body(shape, '-Z')}, sites)
