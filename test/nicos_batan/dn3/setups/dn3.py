description = 'Simulated DN3 instrument'

includes = ['stdsystem']

sysconfig = dict(
    datasinks = ['dn3sink'],
)

# includes = ['monochromator']  # 'source']

devices = dict(
    tths = device('nicos.devices.generic.Axis',
        fmtstr = '%.2f',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-170, 8),
        ),
        precision = 0.05,
    ),
    dn3sink = device('nicos_batan.dn3.devices.datasinks.DN3Sink',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.txt'],
        detectors = ['adet'],
    ),
    mon = device('nicos.devices.generic.VirtualCounter',
        fmtstr = '%d',
        type = 'monitor',
        visibility = (),
    ),
    tim = device('nicos.devices.generic.VirtualTimer',
        fmtstr = '%.2f',
        unit = 's',
        visibility = (),
    ),
    image = device('nicos.devices.generic.VirtualImage',
        fmtstr = '%d',
        pollinterval = 86400,
        size = (32, 1),
        visibility = (),
    ),
    basedet = device('nicos.devices.generic.Detector',
        timers = ['tim'],
        monitors = ['mon'],
        counters = [],
        images = ['image'],
        maxage = 86400,
        pollinterval = None,
        visibility = (),
    ),
    adet = device('nicos_mlz.spodi.devices.Detector',
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
