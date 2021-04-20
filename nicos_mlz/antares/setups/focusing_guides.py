description = 'Focusing guides translation x'

group = 'optional'

tango_base = "tango://antareshw.antares.frm2.tum.de:10000/antares/"

devices = dict(
    gtx = device('nicos.devices.entangle.Motor',
        description = 'Focusing guides translation x',
        tangodevice = tango_base + 'copley/m08',
        abslimits = (0, 75),
        precision = 0.01,
    ),
)
