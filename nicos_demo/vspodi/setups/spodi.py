description = 'Virtual SPODI instrument'

group = 'basic'

includes = [
    'system', 'sampletable', 'detector', 'slits', 'filter', 'mono', 'reactor',
    'nguide',
]

devices = dict(
    wav = device('nicos_mlz.spodi.devices.wavelength.Wavelength',
        description = 'The incoming wavelength',
        unit = 'AA',
        omgm = 'omgm',
        tthm = 'tthm',
        crystal = 'crystal',
        plane = '551',
        fmtstr = '%.3f',
        abslimits = (0.5, 3.0),
    ),
    crystal = device('nicos.devices.generic.ManualSwitch',
        description = 'Monochromator crystal',
        states = ['Ge',]
    ),
)
