description = 'ZWO CCD camera 1 devices'

group = 'optional'

includes = ['shutters', 'filesavers']

tango_base = 'tango://zwo01:10000/zwo/camera/'

devices = dict(
    zwo01 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera',
        tangodevice = tango_base + '1',
        lowlevel = True,
        flip = (True, False),
    ),
    timer_zwo01 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + '1',
        lowlevel = True,
    ),
    det_zwo01 = device('nicos.devices.generic.Detector',
        description = 'Camera base detector',
        images = ['zwo01'],
        timers = ['timer_zwo01'],
    ),
    temp_zwo01 = device('nicos.devices.vendor.lima.ZwoTC',
        description = 'Temperature of the CCD sensor chip',
        tangodevice = tango_base + 'cooler',
        abslimits = (-30, 30),
        precision = 0.5,
        unit = 'degC',
    ),
)

startupcode = '''
SetDetectors(det_zwo01)
'''
