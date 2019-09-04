description = 'Axels diamond setup'

group = 'optional'

tango_base = "tango://antareshw.antares.frm2.tum.de:10000/antares/"

devices = dict(
    lin = device('nicos.devices.tango.Motor',
        description = 'linear axis',
        tangodevice = tango_base + 'copley/m10',
        abslimits = (-25, 25),
        userlimits = (-25, 25),
    ),
    rot = device('nicos.devices.tango.Motor',
        description = 'rotation axis',
        tangodevice = tango_base + 'copley/m11',
        abslimits = (-99999, 99999),
        userlimits = (-99999, 99999),
    ),
)
