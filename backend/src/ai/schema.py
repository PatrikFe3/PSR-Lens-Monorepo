from typing import Annotated, Literal, Union

from pydantic import Field, create_model

ID = r'^[a-z][a-z0-9_]*$'
SITE_REF = r'^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$'

def _choice(values):
    values = tuple(values)
    if not values:
        raise ValueError('The catalog is empty for one of hardware / interfaces.')
    return Literal[values]

def design_spec_model(catalog, templates):
    hardware_ref = _choice(catalog.hardware.ids())
    interface_ref = _choice(catalog.interfaces.ids())
    part_models = tuple(
        create_model(f'Part_{t.name}',
                     id=(str, Field(pattern=ID)),
                     template=(Literal[t.name], ...),
                     params=(t.Params, ...))
        for t in templates.values())
    part = (Annotated[Union[part_models], Field(discriminator='template')]
            if len(part_models) > 1 else part_models[0])
    hardware_use = create_model('HardwareUse', id=(str, Field(pattern=ID)), ref=(hardware_ref, ...))
    connection = create_model(
        'Connection',
        a=(str, Field(pattern=SITE_REF)),
        b=(str, Field(pattern=SITE_REF)),
        kind=(Literal['fixed', 'revolute'], ...),
        interface=(interface_ref | None, None),
        range_deg=(tuple[float, float] | None, None),
        rest_deg=(float, 0.0),
    )
    return create_model(
        'DesignSpecAI',
        intent=(str, ...),
        hardware=(list[hardware_use], ...),
        parts=(list[part], Field(min_length=1)),
        connections=(list[connection], ...),
        assumptions=(list[str], ...),
        questions=(list[str], ...),
    )

