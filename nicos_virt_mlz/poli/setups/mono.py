description = 'POLI monochromator devices'

group = 'lowlevel'

devices = dict(
    wavelength = device('nicos.devices.generic.ManualSwitch',
        description = 'monochromator wavelength',
        unit = 'A',
        states = [1.15, 0.9, 0.7, 0.55],
    ),
)
