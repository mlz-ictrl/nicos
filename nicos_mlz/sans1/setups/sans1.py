description = 'basic sans1 setup'

group = 'basic'

includes = ['collimation', 'detector', 'sample_table_1', 'det1',
            'pressure', 'astrium', 'memograph',
            'manual', 'guidehall', 'pressure_filter',
            'slit', 'selector_tower']

excludes = ['tisane']

sysconfig = dict(
    datasinks = ['Histogram']
)

devices = dict(
    det1 = device('nicos.devices.generic.Detector',
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
