description = 'ZWO CCD camera 2 devices'

group = 'lowlevel'

tango_base = 'tango://zwo02:10000/lima/zwo/'

devices = dict(
    zwo02 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera 2',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
        flip = (True, False),
    ),
    timer_zwo02 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
    ),
    det_zwo02 = device('nicos.devices.generic.Detector',
        description = 'Camera 2 base detector',
        images = ['zwo02'],
        timers = ['timer_zwo02'],
    ),
    temp_zwo02 = device('nicos.devices.vendor.lima.ZwoTC',
        description = 'Temperature of CCD sensor chip cam 2',
        tangodevice = tango_base + 'cooler',
        abslimits = (-30, 30),
        precision = 0.5,
        unit = 'degC',
    ),
)
