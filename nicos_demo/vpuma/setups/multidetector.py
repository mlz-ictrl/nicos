description = 'PUMA multi detector device'

group = 'lowlevel'

import math

excludes = ['detector']

modules = ['nicos_mlz.puma.commands']

level = False

devices = dict(
    med = device('nicos_mlz.puma.devices.multidetector.PumaMultiDetectorLayout',
        description = 'PUMA multi detector',
        rotdetector = ['rd1', 'rd2', 'rd3', 'rd4', 'rd5', 'rd6', 'rd7', 'rd8',
                       'rd9', 'rd10', 'rd11'],
        rotguide = ['rg1', 'rg2', 'rg3', 'rg4', 'rg5', 'rg6', 'rg7', 'rg8',
                    'rg9', 'rg10', 'rg11'],
        att = device('nicos.devices.generic.Axis',
            motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
                abslimits = (-90, 15),
                unit = 'deg',
                refpos = -1,
                fmtstr = '%.3f',
            ),
            precision = 0.01,
        ),
        parkpos = [-15, -17.5, -20., -22.5, -25., -27.5, -30., -32.5, -35.,
                   -37.5, -40.,
                   3.5, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25, 1.0, 0.75, 0.5],
    ),
    monitor = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor',
        fmtstr = '%d',
        type = 'monitor',
        lowlevel = True,
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        lowlevel = True,
        sizes = (1, 11),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Multidetector with single channels',
        timers = ['timer'],
        monitors = ['monitor'],
        images = ['image'],
        # counters = ['ctr1', 'ctr2', 'ctr3', 'ctr4', 'ctr5',
        #             'ctr6', 'ctr7', 'ctr8', 'ctr9', 'ctr10',
        #             'ctr11'],
        maxage = 86400,
        pollinterval = None,
    ),
)

for i in range(11):
    devices['rd%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        description = 'Rotation detector %d multidetector' % (i + 1),
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-42 + (11 - (i + 1)) * 2.5, 13 - i * 2.4),
            unit = 'deg',
            refpos = -13.5 - i * 2.5,
            fmtstr = '%.3f',
            speed = 3,
        ),
        precision = 0.01,
        lowlevel = level,
    )
    devices['rg%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        description = 'Rotation guide %d multidetector' % (i + 1),
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-8, 25),
            unit = 'deg',
            refpos = -7.7,
            fmtstr = '%.3f',
            speed = 1,
        ),
        precision = 0.01,
        lowlevel = level,
    )
    devices['ctr%d' % (i + 1)] = device('nicos.devices.generic.VirtualCounter',
        lowlevel = True,
        type = 'counter',
        countrate = 1 + int(2000 * math.exp(-((i + 1) - 6) ** 2 / 2.)),
        fmtstr = '%d',
    )

startupcode = '''
SetDetectors(det)
'''
