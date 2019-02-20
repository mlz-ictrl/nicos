description = 'PGAA setup with Huber sample table'

group = 'basic'

sysconfig = dict(
    datasinks = ['mcasink', 'chnsink', 'csvsink', 'livesink']
)

includes = [
    'system',
    'reactor',
    'nl4b',
    'pressure',
    'sampletable',
    'pilz',
    'detector',
    'collimation',
]

devices = dict(
    mcasink = device('nicos_mlz.pgaa.devices.MCASink',
        settypes = set(['point']),
        detectors = ['_60p', 'LEGe'],
    ),
    chnsink = device('nicos_mlz.pgaa.devices.CHNSink',
        settypes = set(['point']),
        detectors = ['_60p', 'LEGe'],
    ),
    csvsink = device('nicos_mlz.pgaa.devices.CSVDataSink',
        settypes = set(['point']),
    ),
)

startupcode = """
SetDetectors('_60p', 'LEGe')
SetEnvironment(chamber_pressure)
"""
