description = 'Sample manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    transm = device('nicos.devices.tango.Motor',
        description = 'Sample translation motor',
        tangodevice = tango_base + 'x/motor',
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    trans = device('nicos.devices.generic.Axis',
        description = 'Sample translation',
        motor = 'transm',
        precision = 0.01,
    ),
    rotm = device('nicos.devices.tango.Motor',
        description = 'Sample rotation motor',
        tangodevice = tango_base + 'rot/motor',
        unit = 'deg',
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    rot = device('nicos.devices.generic.Axis',
        description = 'Sample rotation',
        motor = 'rotm',
        precision = 0.01,
    ),
)
