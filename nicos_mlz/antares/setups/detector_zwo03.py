description = 'ZWO CCD camera 3 devices'

group = 'lowlevel'

tango_base = 'tango://zwo03:10000/zwo/camera/'

devices = dict(
    zwo03 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera 3',
        tangodevice = tango_base + '1',
        lowlevel = True,
        flip = (True, False),
    ),
    timer_zwo03 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + '1',
        lowlevel = True,
    ),
    det_zwo03 = device('nicos.devices.generic.Detector',
        description = 'Camera 3 base detector',
        images = ['zwo03'],
        timers = ['timer_zwo03'],
    ),
    temp_zwo03 = device('nicos.devices.vendor.lima.ZwoTC',
        description = 'Temperature of CCD sensor chip cam 3',
        tangodevice = tango_base + 'cooler',
        abslimits = (-30, 30),
        precision = 0.5,
        unit = 'degC',
    ),
)
