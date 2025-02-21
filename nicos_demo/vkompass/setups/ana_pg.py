description = 'PG Analyzer focus devices'

group = 'lowlevel'
excludes = ['ana_heusler']

devices = dict(
    afh = device('nicos.devices.generic.Axis',
        description = 'horizontal focus of pg ana',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-180, 180),
            unit = 'deg',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    ),
    afv = device('nicos.devices.generic.Axis',
        description = 'vertical focus of pg ana',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-180, 180),
            unit = 'deg',
        ),
        fmtstr = '%.3f',
        precision = 0.001,
    ),
)
