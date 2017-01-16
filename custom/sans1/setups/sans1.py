description = 'basic sans1 setup'

group = 'basic'

includes = ['collimation', 'detector', 'sample_table_1', 'det1',
            'pressure', 'selector_tower', 'astrium', 'memograph',
            'manual', 'guidehall', 'outerworld', 'pressure_filter',
            'slit']

excludes = ['tisane']

sysconfig = dict(
    datasinks = ['Histogram',]
)

devices = dict(
    det1    = device('devices.generic.Detector',
                     description = 'QMesyDAQ Image type Detector1',
                     timers = ['det1_timer'],
                     counters = [],
                     monitors = ['det1_mon1', 'det1_mon2'],
                     images = ['det1_image'],
                     liveinterval = 30.0,
                    ),
)

startupcode = '''
det1._attached_images[0].listmode = False
'''
