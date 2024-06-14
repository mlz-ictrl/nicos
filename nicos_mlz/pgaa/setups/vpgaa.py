description = 'PGAA setup with sample changer'

group = 'basic'

sysconfig = dict(
    datasinks = ['mcasink', 'chnsink', 'csvsink', 'livesink']
)

includes = [
    'system',
    'reactor',
    'nl4b',
    'pressure',
    'samplechanger',
    'pilz',
    'vdetector',
    'collimation',
]

devices = dict(
    mcasink = device('nicos_mlz.pgaa.datasinks.MCASink',
        settypes = {'point'},
        detectors = ['_60p', 'LEGe'],
    ),
    chnsink = device('nicos_mlz.pgaa.datasinks.CHNSink',
        settypes = {'point'},
        detectors = ['_60p', 'LEGe'],
    ),
    csvsink = device('nicos_mlz.pgaa.datasinks.CSVDataSink',
        settypes = {'point'},
    ),
)

startupcode = """
SetDetectors('_60p', 'LEGe')
SetEnvironment(chamber_pressure)
"""
