description = 'Philipps Polarizer Setup'

group = 'optional'

tango_base = "tango://antareshw.antares.frm2.tum.de:10000/antares/"

devices = dict(
    pry = device('nicos.devices.tango.Motor',
        description = 'Polarizer Rotation around Y',
        tangodevice = tango_base + 'copley/m05',
        abslimits = (-400, 400),
        precision = 0.01,
    ),
    ptx = device('nicos.devices.tango.Motor',
        description = 'Polarizer Translation X',
        tangodevice = tango_base + 'copley/m06',
        abslimits = (-20, 20),
        precision = 0.01,
    ),
)
