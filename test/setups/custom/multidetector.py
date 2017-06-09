
devices = dict(
    med = device('nicos_mlz.puma.devices.multidetector.PumaMultiDetectorLayout',
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
    ),
)

for i in range(11):
    devices['rd%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-37 - (i + 1 - 11) * 2.5 , 11 - i * 2.5),
            unit = 'deg',
            refpos = 0,
            fmtstr = '%.3f',
        ),
        precision = 0.01,
    )
    devices['rg%d' % (i + 1)] = device('nicos.devices.generic.Axis',
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-45, 5),
            unit = 'deg',
            refpos = 0,
            fmtstr = '%.3f',
        ),
        precision = 0.01,
    )
