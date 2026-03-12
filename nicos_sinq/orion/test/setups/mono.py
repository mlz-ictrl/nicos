devices = dict(
    mom1 = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        fmtstr = '%.3f',
        abslimits = (0, 35),
    ),
    mono = device('nicos_sinq.orion.devices.MonoSwitcher',
        description = 'monochromator',
        moveable = 'mom1',
        mapping = {
            3.3: 2.08,
            1.73: 31.49,
            1.32: 21.25,
        },
        precision = .01,
        unit = 'A',
    ),
)
