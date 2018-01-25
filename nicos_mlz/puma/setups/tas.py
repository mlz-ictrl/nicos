description = 'PUMA triple-axis setup with FRM2-Detector'

includes = ['pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers',
            'detector',]

group = 'basic'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    det = device('nicos.devices.generic.Detector',
        # description = 'Puma detector device (5 counters)',
        description = 'Puma detector QMesydaq device (3 counters)',
        timers = ['timer'],
        # monitors = ['mon1', 'mon2'],
        monitors = ['mon1'],
        # counters = ['det1', 'det2', 'det3', 'det4', 'det5'],
        counters = ['det1', 'det2', 'det3'],
        images = [],
        maxage = 1,
        pollinterval = 1,
    ),
)

startupcode = '''
SetDetectors(det)
'''
