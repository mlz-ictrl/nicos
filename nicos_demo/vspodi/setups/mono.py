description = 'Monochromator device setup'

group = 'lowlevel'

devices = dict(
    omgm = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated OMGM',
        fmtstr = '%.3f',
        unit = 'deg',
        abslimits = (-40, 80),
        speed = 1,
    ),
    tthm = device('nicos.devices.generic.ManualSwitch',
        description = 'HWB TTHM',
        fmtstr = '%.3f',
        unit = 'deg',
        states = (155.,),
    ),
    # tthm = device('nicos.devices.generic.VirtualMotor',
    #     description = 'virtual TTHM',
    #     fmtstr = '%.2f',
    #     unit = 'deg',
    #     abslimits = (-200, 200),
    #     speed = 2,
    # ),
)
