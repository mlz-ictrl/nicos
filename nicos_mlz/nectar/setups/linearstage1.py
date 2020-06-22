description = 'Additional linear stage'

group = 'optional'

tango_base = 'tango://nectarhw.nectar.frm2.tum.de:10000/nectar'

devices = dict(
    linst1_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + '/cam/fov',
        abslimits = (0.0001, 900),
        comtries = 3,
        lowlevel = True,
    ),
    linst1 = device('nicos.devices.generic.Axis',
        description = 'Free useable linear stage',
        pollinterval = 5,
        maxage = 12,
        fmtstr = '%.2f',
        userlimits = (0.0001, 900),
        precision = 0.1,
        motor = 'linst1_m',
    ),
)
