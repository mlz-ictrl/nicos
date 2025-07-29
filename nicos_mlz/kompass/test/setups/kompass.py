description = 'Kompass test setups'

devices = dict(
    stt_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.4f',
        visibility = (),
        unit = 'deg',
        abslimits = (-40, 40),
    ),
    pbs = device('nicos.devices.generic.ManualSwitch',
        states = ['down', 'up'],
    ),
    stt = device('nicos_mlz.kompass.devices.SttWithPBS',
        stt = 'stt_m',
        pbs = 'pbs',
        limits = (-30, 38),
        pbs_values = ('down', 'up'),
    ),
)
