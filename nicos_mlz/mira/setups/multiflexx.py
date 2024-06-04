description = 'Multiflex detector setup'

group = 'lowlevel'

excludes = ['detector']

tango_base = 'tango://mesydaq.mira.frm2.tum.de:10000/qm/qmesydaq/'

devices = dict(
    timer = device('nicos.devices.entangle.TimerChannel',
        description = 'QMesyDAQ timer',
        tangodevice = tango_base + 'timer',
        fmtstr = '%.2f',
        visibility = (),
    ),
    mon1 = device('nicos.devices.entangle.CounterChannel',
        description = 'QMesyDAQ monitor 1',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
        fmtstr = '%d',
        visibility = (),
    ),
    image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'QMesyDAQ Image',
        tangodevice = tango_base + 'image',
        visibility = (),
    ),
    channels = device('nicos.devices.vendor.qmesydaq.tango.MultiCounter',
        tangodevice = tango_base + 'image',
        visibility = (),
        # channels = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        channels = list(range(1, 156)),
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'MultiFlexx detector QMesydaq device (155 counters)',
        timers = ['timer'],
        monitors = ['mon1'],
        counters = ['channels'],
        images = [],
        maxage = None,
        pollinterval = None,
    ),
)

startupcode = '''
SetDetectors(det)
'''
