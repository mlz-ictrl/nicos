description = 'Keyence readout'

group = 'lowlevel'

devices = dict(
    keyence = device('nicos_mlz.labs.spodi.bio.devices.keyence.KeyenceImage',
        visibility = {'metadata', 'namespace'},
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        visibility = {'metadata', 'namespace'},
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Detector',
        images = ['keyence'],
        timers = ['tim1'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
