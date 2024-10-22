description = 'Microscope webcam 1'
group = 'optional'

sysconfig = dict(
    datasinks = ['jpg'],# 'live'],
)

devices = dict(
    image = device('nicos_mgml.smaract.devices.webcam.Webcam',
        description = 'Main smaract microscope',
        device = 0,
    ),
    jpg = device('nicos_mgml.smaract.devices.webcam.JPGImageSink',
        description = 'jpeg sink',
        filenametemplate = ['%(pointcounter)08d.jpg'],
        subdir = '',
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer',
        visibility = (),
    ),
    cam1 = device('nicos.devices.generic.Detector',
        description = 'camera device',
        timers = ['timer'],
        images = ['image'],
        counters = [],
    ),
)
