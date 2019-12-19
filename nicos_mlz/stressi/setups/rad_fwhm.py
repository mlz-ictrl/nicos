description = 'Full width at half maximum radial collimator'

group = 'lowlevel'

devices = dict(
    rad_fwhm = device('nicos.devices.generic.ManualSwitch',
        description = 'FWHM Radialcollimator',
        fmtstr = '%.1f',
        unit = 'mm',
	states = (0.5, 1, 2, 5, 10, 20),
        requires = {'level': 'admin'},
    ),
)
