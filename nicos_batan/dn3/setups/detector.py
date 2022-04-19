description = 'Simulated DN3 instrument'

group = 'lowlevel'

devices = dict(
    mon = device('nicos.devices.generic.VirtualCounter',
        description = 'Simulated Monitor Detector',
        fmtstr = '%d',
        type = 'monitor',
        visibility = (),
    ),
    tim = device('nicos.devices.generic.VirtualTimer',
        description = 'Simulated Timer',
        fmtstr = '%.2f',
        unit = 's',
        visibility = (),
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        size = (32, 1),
        visibility = (),
    ),
    basedet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim'],
        monitors = ['mon'],
        counters = [],
        images = ['image'],
        maxage = 86400,
        pollinterval = None,
        visibility = (),
    ),
    adet = device('nicos_mlz.spodi.devices.Detector',
        description = 'Scanning (resolution steps) detector',
        motor = 'tths',
        detector = 'basedet',
        pollinterval = None,
        maxage = 86400,
        liveinterval = 5,
        range = 5.,
        numinputs = 32,
        resosteps = 100,
    ),
)

startupcode = '''
SetDetectors(adet)
'''
