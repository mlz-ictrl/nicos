description = 'Simulated HRPD instrument'

group = 'lowlevel'

excludes = []

includes = []

devices = dict(
    mon = device('nicos.devices.generic.VirtualCounter',
        description = 'Simulated Monitor Detector',
        fmtstr = '%d',
        type = 'monitor',
        lowlevel = True,
    ),
    tim = device('nicos.devices.generic.VirtualTimer',
        description = 'Simulated Timer',
        fmtstr = '%.2f',
        unit = 's',
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        lowlevel = True,
        sizes = (32, 1),
    ),
    basedet = device('nicos.devices.generic.Detector',
        description = 'Classical detector with single channels',
        timers = ['tim'],
        monitors = ['mon'],
        counters = [],
        images = ['image'],
        maxage = 86400,
        pollinterval = None,
        lowlevel = True,
    ),
    adet = device('spodi.detector.Detector',
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
