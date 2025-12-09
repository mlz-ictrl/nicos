description = 'Setup for the FastcomTec MCA coming with the mobile ' \
              'chopper unit'

group = 'basic'

includes = [
    'el737',
]

counterprefix = 'SQ:BOA:counter'

devices = dict(
    el737 = device('nicos_sinq.devices.epics.sinqdaq.SinqDetector',
        description = 'Detector Nicos Device',
        timers = ['elapsedtime'],
        monitors = ['hardware_preset', 'monitorval', 'protoncurr'],
        liveinterval = 20,
        saveintervals = [60],
        visibility = {'metadata', 'namespace'},
    ),
    fastcomtec = device('nicos_sinq.boa.devices.fastcomtec.FastComtecChannel',
        description = 'FastComtec MCA channel',
        pvprefix = 'SQ:BOA:mca',
    ),
    fcdet = device('nicos.devices.generic.detector.Detector',
        description = 'Dummy detector to encapsulate fastcomtec',
        monitors = [
            'fastcomtec',
        ],
        timers = [
            'fastcomtec',
        ],
        images = [
            'fastcomtec',
        ],
        visibility = ()
    ),
    boadet = device('nicos_sinq.devices.detector.ControlDetector',
        description = 'Fastcomtec detector coordination',
        trigger = 'el737',
        followers = ['fcdet'],
    )
)

startupcode = '''
SetDetectors(boadet)
'''
