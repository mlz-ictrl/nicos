description = 'complete measurement'

includes = ['detector', 'chopper', 'chdelay', 'voltage', 'safety', 'vacuum', 'power', 'rc', 'slit', 'table']

devices = dict(
    m = device('nicos.toftof.measurement.TofTofMeasurement',
               chopper = 'chController',
               chdelay = 'chdelay',
               counter = 'det'),
)
