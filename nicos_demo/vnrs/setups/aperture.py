description = 'Instrument aperture'

group = 'lowlevel'

devices = dict(
    aperture = device('nicos.devices.generic.ManualSwitch',
        description = 'Instrument aperture L/D',
        states = (185, 300, 700),
        fmtstr = '%d',
    ),
)
