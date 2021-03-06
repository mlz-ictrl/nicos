description = 'Detector CARESS HWB Devices'

group = 'lowlevel'

devices = dict(
    mon = device('nicos.devices.generic.VirtualCounter',
        description = 'Simulated MON',
        fmtstr = '%d',
        type = 'monitor',
        lowlevel = True,
    ),
    tim1 = device('nicos.devices.generic.VirtualTimer',
        description = 'Simulated TIM1',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    t_mon = device('nicos.devices.generic.VirtualCounter',
        description = 'HWB MON Transmission Monitor',
        fmtstr = '%d',
        type = 'monitor',
        countrate = 100,
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        lowlevel = True,
        sizes = (256, 256),
    ),
    roi = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI',
        roi = (122, 50, 12, 140),
    ),
    adet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim1'],
        monitors = ['mon'],
        counters = ['t_mon', 'roi',],
        images = ['image'],
        pollinterval = None,
        liveinterval = 0.5,
        postprocess = [
            ('roi', 'image'),
        ],
    ),
    ysd = device('nicos.devices.generic.ManualMove',
        description = 'distance sample detector',
        default = 100.,
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (0, 1100.),
    ),
    hv1 = device('nicos.devices.generic.VirtualMotor',
        description = 'HV power supply 1',
        requires = {'level': 'admin'},
        abslimits = (0, 3200),
        speed = 2,
        fmtstr = '%.1f',
        unit = 'V',
        curvalue = 3100,
    ),
    hv2 = device('nicos.devices.generic.VirtualMotor',
        description = 'HV power supply 2',
        requires = {'level': 'admin'},
        abslimits = (-2500, 0),
        speed = 2,
        fmtstr = '%.1f',
        unit = 'V',
        curvalue = -2400,
    ),
)
