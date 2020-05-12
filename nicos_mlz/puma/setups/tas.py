description = 'PUMA triple-axis setup with FRM2-Detector'

includes = ['pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers',
            'detector',]

group = 'basic'

devices = dict(
    det = device('nicos.devices.generic.Detector',
        # description = 'Puma detector device (5 counters)',
        description = 'Puma detector QMesydaq device (3 counters)',
        timers = ['timer'],
        monitors = ['mon1'],  # + ['mon2'],
        counters = ['det1', 'det2', 'det3'],  # + ['det4', 'det5'],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
