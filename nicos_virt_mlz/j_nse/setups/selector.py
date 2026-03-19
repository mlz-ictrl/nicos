description = 'setup for the velocity selector'
group = 'optional'

includes = [
    'counter',
]

devices = dict(
    selector_lambda = device('nicos.devices.generic.virtual.VirtualMotor',
        description = 'Selector wavelength control',
        userlimits = (6, 14),
        abslimits = (6, 14),
        unit = 'Å',
        fmtstr = '%.2f',
        pollinterval = 0.5,
    ),
    selector_speed = device(
        'nicos_mlz.refsans.devices.converters.LinearKorr',
        description = 'Selector speed',
        unit = 'rpm',
        informula = '60 * x',
        dev = 'selector',
    ),
)
