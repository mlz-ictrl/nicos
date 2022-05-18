description = 'Q range displaying devices'

group = 'lowlevel'

includes = ['detector', 'det1', 'sans1_det', 'alias_lambda']

devices = dict(
    QRange = device('nicos_mlz.sans1.devices.resolution.Resolution',
        description = 'Current q range',
        detector = 'det1',
        beamstop = 'bs1',
        wavelength = 'wl',
        detpos = 'det1_z',
    ),
)
