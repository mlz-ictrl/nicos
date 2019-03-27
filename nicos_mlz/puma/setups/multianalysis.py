description = 'Classical multianalysis setup'

group = 'basic'

includes = ['pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers',
            'multidet', 'multiana', 'cad', 'opticalbench', 'detector']

excludes = ['tas', 'defcal', 'polarization']

nethost = 'pumasrv.puma.frm2'

devices = dict(
    det = device('nicos.devices.generic.Detector',
        description = 'Puma detector QMesydaq device (11 counters)',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = [],  # ['channels'],
        images = ['image'],
        maxage = 86400,
        pollinterval = None,
    ),
)

startupcode = '''
SetDetectors(det)
med.opmode = 'multi'
'''
