description = 'complete measurement'

includes = ['detector', 'chopper', 'chdelay', 'voltage', 'safety', 'vacuum', 'power']
includes += ['table', 'rc', 'slit']

devices = dict(
    m = device('nicos.toftof.measurement.TofTofMeasurement',
               chopper = 'ch',
               chdelay = 'chdelay',
               counter = 'det'),
)
