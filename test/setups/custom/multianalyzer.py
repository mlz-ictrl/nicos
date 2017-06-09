
devices = dict(
    man = device('nicos_mlz.puma.devices.multianalyzer.PumaMultiAnalyzer',
        translations = ['ta1', 'ta2', 'ta3', 'ta4', 'ta5', 'ta6', 'ta7', 'ta8',
                        'ta9', 'ta10', 'ta11'],
        rotations = ['ra1', 'ra2', 'ra3', 'ra4', 'ra5', 'ra6', 'ra7', 'ra8',
                     'ra9', 'ra10', 'ra11'],
    ),
)

for i in range(1, 12):
    devices['ta%d' % i] = device('nicos.devices.generic.Axis',
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-0.1, 250.1),
            userlimits = (-0.001, 250.001),
            unit = 'mm',
            refpos = 0.,
            fmtstr = '%.3f',
        ),
        precision = 0.01,
    )
    devices['ra%d' % i] = device('nicos.devices.generic.Axis',
        motor = device('nicos_mlz.puma.devices.virtual.VirtualReferenceMotor',
            abslimits = (-60.1, 0.1),
            userlimits = (-60.05, 0.1),
            unit = 'deg',
            refpos = 0.1,
            fmtstr = '%.3f',
        ),
        precision = 0.01,
    )
