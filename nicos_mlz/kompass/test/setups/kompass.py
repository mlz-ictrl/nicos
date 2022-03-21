description = 'Kompass test setups'

devices = dict(
    stt_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.4f',
        visibility = (),
        unit = 'deg',
        abslimits = (-40, 40),
    ),
    stt_ax = device('nicos.devices.generic.Axis',
        motor = 'stt_m',
        fmtstr = '%.3f',
        precision = 0.001,
    ),
    pbs = device('nicos.devices.generic.ManualSwitch',
        states = ['down', 'up'],
    ),
    stt = device('nicos_mlz.kompass.devices.SttWithPBS',
        stt = 'stt_ax',
        pbs = 'pbs',
        limits = (-30, 38),
        pbs_values = ('down', 'up'),
    ),
)
