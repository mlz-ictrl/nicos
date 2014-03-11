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
               description = 'Measurement object',
               detinfofile = '/users/data/detinfo.dat',
               # filecounter = '/users/data/counter',
               timechannels = 4096,
               chopper = 'ch',
               chdelay = 'chdelay',
               counter = 'det',
               fileformats = [],
              ),
)

startupcode = """
SetDetectors(m)
"""
