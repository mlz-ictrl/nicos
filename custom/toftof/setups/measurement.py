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
    'collimator',
    'rc',
    'samplememograph',
]

devices = dict(
    m = device('toftof.measurement.TofTofMeasurement',
               description = 'Measurement object',
               detinfofile = '/data/detinfo.dat',
               # filecounter = '/data/counter',
               timechannels = 4096,
               chopper = 'ch',
               chdelay = 'chdelay',
               counter = 'det',
               rc = 'rc_motor',
               filenametemplate = '%06d_0000.raw',
              ),
)

startupcode = '''
SetDetectors(m)
'''
