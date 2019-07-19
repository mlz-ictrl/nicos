description = 'basic sans1 setup'

group = 'basic'

includes = ['collimation', 'detector', 'sample_table_1', 'det1',
            'pressure', 'memograph',
            'manual',
            # 'guidehall',
            'pressure_filter',
            'slit', 'selector_tower', 'chopper_phase',
            # 'nl4a'
            ]

excludes = ['tisane']

sysconfig = dict(
    # datasinks = ['Histogram'],
)

devices = dict(
    det1 = device('nicos_mlz.sans1.devices.detector.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['det1_timer'],
        counters = [],
        monitors = ['det1_mon1', 'det1_mon2'],
        images = ['det1_image'],
        liveinterval = 30.0,
    ),
)

startupcode = '''
# det1._attached_images[0].listmode = False
'''
