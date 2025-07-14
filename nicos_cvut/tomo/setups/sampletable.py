description = 'Sample manipulation stage'

group = 'lowlevel'

tango_base = 'tango://192.168.168.1:10000/tomo/'

devices = dict(
    sample_trans_m = device('nicos.devices.entangle.Motor',
        description = 'Sample translation motor',
        tangodevice = tango_base + 'translation/motor',
        unit = 'mm',
        fmtstr = '%.2f',
        visibility = (),
    ),
    sample_x = device('nicos.devices.generic.Axis',
        description = 'Sample translation',
        motor = 'sample_trans_m',
        precision = 0.01,
    ),
    rotm = device('nicos.devices.entangle.Motor',
        description = 'Sample rotation motor',
        tangodevice = tango_base + 'rotation/motor',
        unit = 'deg',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rot = device('nicos.devices.generic.Axis',
        description = 'Sample rotation',
        motor = 'rotm',
        precision = 0.05,
    ),
)
