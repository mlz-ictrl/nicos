description = 'STRESS-SPEC setup with Eulerian cradle'

group = 'basic'

includes = [
    'system', 'monochromator', 'detector', 'sampletable', 'primaryslit',
    'slits', 'reactor'
]

excludes = ['stressi', 'robot']

sysconfig = dict(
        datasinks = ['caresssink'],
)

devices = dict(
    chis = device('nicos.devices.generic.Axis',
        description = 'Simulated CHIS axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.2f',
            unit = 'deg',
            abslimits = (-180, 180),
            lowlevel = True,
            speed = 2,
        ),
        precision = 0.001,
    ),
    phis = device('nicos.devices.generic.Axis',
        description = 'Simulated PHIS axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.2f',
            unit = 'deg',
            abslimits = (-720, 720),
            lowlevel = True,
            speed = 2,
        ),
        precision = 0.001,
    ),
)
