description = 'Beam monochromating devices'

includes = ['motor']

devices = dict(
    mono = device('nicos.devices.generic.CrystalMonochromator',
        description = 'Crystal monochromator',
        theta = 'theta_monochromator',
        twotheta = 'theta2_selectorarm',
        material = 'PG',
        reflection = (0, 0, 2),
    ),
)
