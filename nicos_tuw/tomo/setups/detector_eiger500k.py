description = 'Dectris Eiger2 500k'
group = 'optional'

includes = ['filesavers']

tango_base = 'tango://localhost:10000/lima/'

devices = dict(
    eiger = device('nicos.devices.vendor.lima.EigerLimaCCD',
        description = 'Dectris Eiger2 500k',
        tangodevice = tango_base + 'limaccd/1',
        hwdevice = tango_base + 'limaccd/eiger',
    ),
    timer_eiger = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = "The camera's internal timer",
        tangodevice = tango_base + 'limaccd/1',
    ),
    det_eiger = device('nicos.devices.generic.Detector',
        description = 'Dectris Eiger2 500k',
        images = ['eiger'],
        timers = ['timer_eiger'],
    ),

)

startupcode = '''
SetDetectors(det_eiger)

## override hw setting to known good values.
eiger.rotation = 180
eiger.photon_energy = 17450
'''
