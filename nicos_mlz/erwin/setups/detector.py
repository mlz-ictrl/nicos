description = 'Standard CHARM detector'

group = 'optional'

includes = ['charmbox02']

tango_host = 'erwindet.erwin.frm2.tum.de'

tango_base = f'tango://{tango_host}:10000/qm/qmesydaq/'

sysconfig = dict(
    datasinks = ['histogram', 'listmode'],
)

devices = dict(
    mon1 = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Monitor 1 at big charm detector',
        tangodevice = tango_base + 'counter0',
        type = 'monitor',
    ),
    events = device('nicos.devices.vendor.qmesydaq.tango.CounterChannel',
        description = 'Event counter at big charm detector',
        tangodevice = tango_base + 'events',
        type = 'other',
    ),
    image = device('nicos.devices.vendor.qmesydaq.tango.ImageChannel',
        description = 'Image at big charm detector',
        tangodevice = tango_base + 'image',
    ),
    timer = device('nicos.devices.vendor.qmesydaq.tango.TimerChannel',
        description = 'Timer at big charm detector',
        tangodevice = tango_base + 'timer',
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'Big charm detector',
        images = ['image'],
        monitors = ['mon1'],
        timers = ['timer'],
        liveinterval = 1.0,
    ),
    histogram = device('nicos_mlz.devices.datasinks.qmesydaq.HistogramSink',
        description = 'Histogram data written via QMesyDAQ',
        image = 'image',
        subdir = 'mtxt',
        filenametemplate = ['%(pointcounter)08d.mtxt'],
    ),
    listmode = device('nicos_mlz.devices.datasinks.qmesydaq.ListmodeSink',
        description = 'Listmode data written via QMesyDAQ',
        image = 'image',
        subdir = 'list',
        filenametemplate = ['%(pointcounter)08d.mdat'],
    ),
)
