description = 'Detector devices'

group = 'lowlevel'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        visibility = (),
    ),
    monitor = device('nicos.devices.generic.VirtualCounter',
        visibility = (),
        type = 'monitor',
        countrate = 100,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        visibility = (),
        size = (80, 256),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Detector device with timer, monitor, and image',
        timers = ['timer'],
        monitors = ['monitor'],
        images = ['image'],
    ),
) 
