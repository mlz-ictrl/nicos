description = 'setup for the velocity selector'
group = 'optional'

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
        informula = '16000.0 * 8.0 / x * (0.96151 + 4.877865 / x ** 2.43012)',
        dev = 'selector_lambda',
        fmtstr = '%.0f',
        pollinterval = 0.5,
    ),
)
