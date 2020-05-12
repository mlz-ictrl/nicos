description = 'Classical multianalysis setup'

group = 'basic'

modules = ['nicos_mlz.puma.commands']

includes = ['pumabase',
            # 'seccoll', 'collimation', 'ios', 'hv', 'notifiers',
            'multidetector', 'multianalyzer', 'cad', 'opticalbench',
            # 'detector',
           ]

excludes = ['tas', 'defcal', 'polarization']

# devices = dict(
#     det = device('nicos.devices.generic.Detector',
#         description = 'Puma detector QMesydaq device (11 counters)',
#         timers = ['timer'],
#         monitors = ['mon1'],
#         images = ['image'],
#         maxage = 86400,
#         pollinterval = None,
#     ),
# )

startupcode = '''
SetDetectors(det)
med.opmode = 'multi'
'''
