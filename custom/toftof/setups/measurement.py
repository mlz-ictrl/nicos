description = 'complete measurement'

group = 'basic'

includes = [
    'detector',
    'chopper',
    'vacuum',
    'voltage',
    'safety',
    'reactor',
    'table',
    'slit',
]

devices = dict(
    m = device('toftof.measurement.TofTofMeasurement',
               detinfofile = '/users/data/detinfo.dat',
               timechannels = 4096,
               chopper = 'ch',
               chdelay = 'chdelay',
               counter = 'det',
              ),
)

startupcode = """
SetDetectors(m)
"""
