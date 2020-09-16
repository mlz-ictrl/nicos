description = 'detector setup'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer for the camera',
    ),
    image = device('nicos.devices.generic.VirtualImage',
        description = 'image for the camera',
    ),
    cam = device('nicos.devices.generic.Detector',
        description = 'ccd camera',
        timers = ['timer'],
        images = ['image'],
    ),
    tifformat = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'saves image data in tiff format',
        detectors = ['cam'],
        filenametemplate = ['%(pointsamplecounter)08d.tiff'],
    ),
)

