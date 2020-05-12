description = 'qmesydaq devices for REFSANS'

# to be included by refsans ?
group = 'optional'

sysconfig = dict(
    datasinks = ['LiveViewSink'],
)

devices = dict(
    # Listmode = device('nicos_mlz.devices.qmesydaqsinks.ListmodeSink',
    #     description = 'Listmode data written via QMesyDAQ',
    #     image = 'image',
    #     subdir = 'list',
    #     filenametemplate = ['%(proposal)s_%(pointcounter)08d.mdat'],
    # ),
    LiveViewSink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    mon1 = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Counter0',
        fmtstr = '%d',
        type = 'monitor',
        countrate = 100,
        # lowlevel = True,
    ),
    mon2 = device('nicos.devices.generic.VirtualCounter',
        description = 'QMesyDAQ Counter1',
        fmtstr = '%d',
        type = 'monitor',
        countrate = 100,
        # lowlevel = True,
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = "The detector's internal timer",
        lowlevel = True,
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'demo 2D detector',
        fmtstr = '%d',
        sizes = (256, 256),
        lowlevel = True,
    ),
    det = device('nicos.devices.generic.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['timer'],
        monitors = ['mon1', 'mon2'],
        images = ['image'],
    ),
)

startupcode = '''
SetDetectors(det)
'''
