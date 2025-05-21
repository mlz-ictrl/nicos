description = 'Dectris Eiger2 500k'
group = 'optional'

includes = ['filesavers']
excludes = ['detector_eiger500k']

tango_base = 'tango://localhost:10000/lima/'

devices = dict(
    eiger = device('nicos.devices.generic.VirtualImage',
        description = 'Dectris Eiger2 500k (simulated)',
        size = (1028, 512)
    ),
    timer_eiger = device('nicos.devices.generic.VirtualTimer',
        description = "The camera's internal timer (simulated)",
    ),
    det_eiger = device('nicos.devices.generic.Detector',
        description = 'Dectris Eiger2 500k (simulated)',
        images = ['eiger'],
        timers = ['timer_eiger'],
    ),

)

startupcode = '''
SetDetectors(det_eiger)
'''
