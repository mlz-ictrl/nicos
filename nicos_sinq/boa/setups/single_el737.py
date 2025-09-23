description = 'Neutron counter box'

group = 'basic'

includes = [
    'el737',
]

pvprefix = 'SQ:BOA:counter'

devices = dict(
    countval = device(
        'nicos_sinq.devices.epics.sinqdaq.DAQChannel',
        description = 'Detector Counts',
        daqpvprefix = pvprefix,
        channel = 2,
        type = 'monitor',
    ),

    el737 = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Nicos Device',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset', 'countval', 'monitorval', 'protoncurr'],
        liveinterval = 20,
        saveintervals = [60],
    ),
)

startupcode = '''
SetDetectors(el737)
'''
