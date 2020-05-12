description = 'Motor for FOV camera translation in large detector box'

group = 'basic'

includes = ['basic', 'sbl', 'lbl', 'servostar']

tango_base = "tango://antareshw.antares.frm2.tum.de:10000/antares/"

devices = dict(
    ccdtx = device('nicos.devices.tango.Motor',
        description = 'Camera Translation X',
        tangodevice = tango_base + 'copley/m07',
        abslimits = (-9999, 9999),
        userlimits = (-0, 693),
    ),
)
