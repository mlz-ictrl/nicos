description = 'Virtual CHARM detector'

group = 'optional'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Timer at big charm detector',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor 1 at charm detector',
        type = 'monitor',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Big charm detector',
        images = ['image'],
        monitors = ['mon1'],
        timers = ['timer'],
        liveinterval = 1.0,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'demo 2D detector',
        size = (9 * 128, 128),
        fmtstr = '%d',
        pollinterval = None,
    ),
    detsampledist = device('nicos.devices.generic.ManualMove',
        description = 'Distance between sample and detector',
        default = 800,
        abslimits = (800, 800),
        unit = 'mm',
    ),
)

startupcode = """
SetDetectors(det)
"""
