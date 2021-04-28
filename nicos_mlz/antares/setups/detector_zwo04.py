description = 'ZWO CCD camera 4 devices'

group = 'lowlevel'

tango_base = 'tango://zwo04:10000/lima/zwo/'

devices = dict(
    zwo04 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera 4',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
        flip = (True, False),
    ),
    timer_zwo04 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
    ),
    det_zwo04 = device('nicos.devices.generic.Detector',
        description = 'Camera 4 base detector',
        images = ['zwo04'],
        timers = ['timer_zwo04'],
    ),
    # temp_zwo04 = device('nicos.devices.vendor.lima.ZwoTC',
    #     description = 'Temperature of CCD sensor chip cam 4',
    #     tangodevice = tango_base + 'cooler',
    #     abslimits = (-30, 30),
    #     precision = 0.5,
    #     unit = 'degC',
    # ),
)
