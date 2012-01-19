description = 'complete measurement'

includes = ['detector', 'chopper', 'chdelay', 'voltage', 'safety', 'shutter', 'vacuum', 'power']
includes += ['table', 'rc', 'slit']

devices = dict(
    m = device('nicos.toftof.measurement.TofTofMeasurement',
               detinfofile = '/users/data/detinfo.dat',
               chopper = 'ch',
               chdelay = 'chdelay',
               counter = 'det'),
)
