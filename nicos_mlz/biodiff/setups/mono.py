description = 'Beam monochromating devices'

group = 'lowlevel'

includes = ['motor', 'astrium']

devices = dict(
    mono = device('nicos.devices.generic.CrystalMonochromator',
        description = 'Crystal monochromator',
        theta = 'theta_monochromator',
        twotheta = 'theta2_selectorarm',
        material = 'PG',
        reflection = (0, 0, 2),
    ),
    wav = device('nicos_mlz.biodiff.devices.wavelength.WaveLength',
        description = 'Wavelength device',
        device = 'mono',
        lock = 'selector_speed',
        selector = 'selector_lambda',
        unlockvalue = 9000,
    ),
)
