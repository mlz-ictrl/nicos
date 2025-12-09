description = 'Heusler analyzer focus device'

group = 'lowlevel'
excludes = ['ana_pg']

devices = dict(
    # ahfh (Heusler-Analyzer)
    ahfh = device('nicos.devices.generic.VirtualMotor',
        description = 'Horizontal focus of Heusler ana.',
        abslimits = (-180, 180),
        fmtstr = '%.4f',
        unit = 'deg',
    ),
)

startupcode = '''
enable(ahfh)
'''

