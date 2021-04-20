description = 'Sample manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    sample_x_m = device('nicos.devices.entangle.Motor',
        description = 'Sample X translation motor',
        tangodevice = tango_base + 'sample_x/motor',
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    sample_x = device('nicos.devices.generic.Axis',
        description = 'Sample X translation',
        motor = 'sample_x_m',
        precision = 0.01,
    ),
    # sample_y_m = device('nicos.devices.entangle.Motor',
    #     description = 'Sample Y translation motor',
    #     tangodevice = tango_base + 'sample_y/motor',
    #     unit = 'mm',
    #     fmtstr = '%.2f',
    #     lowlevel = True,
    # ),
    # sample_y = device('nicos.devices.generic.Axis',
    #     description = 'Sample Y translation',
    #     motor = 'sample_y_m',
    #     precision = 0.01,
    # ),
    rotm = device('nicos.devices.entangle.Motor',
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
