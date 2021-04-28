description = 'ZWO CCD camera 5 devices'

group = 'lowlevel'

tango_base = 'tango://zwo05:10000/lima/zwo/'

devices = dict(
    zwo05 = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera 5',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
        flip = (True, False),
    ),
    timer_zwo05 = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + 'camera0',
        lowlevel = True,
    ),
    det_zwo05 = device('nicos.devices.generic.Detector',
        description = 'Camera 5 base detector',
        images = ['zwo05'],
        timers = ['timer_zwo05'],
    ),
    # temp_zwo05 = device('nicos.devices.vendor.lima.ZwoTC',
    #     description = 'Temperature of CCD sensor chip cam 1',
    #     tangodevice = tango_base + 'cooler',
    #     abslimits = (-30, 30),
    #     precision = 0.5,
    #     unit = 'degC',
    # ),
)
