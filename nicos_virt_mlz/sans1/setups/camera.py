description = 'neutron camera'
group = 'optional'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer = device('nicos.devices.generic.VirtualTimer',
        description = 'timer for the Neutron camera',
    ),
    camimage = device('nicos.devices.generic.VirtualImage',
        description = 'image for the Neutron camera',
    ),
    cam = device('nicos.devices.generic.Detector',
        description = 'NeutronOptics camera',
        timers = ['camtimer'],
        images = ['camimage'],
    ),
    tifformat = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I',
    ),
)
