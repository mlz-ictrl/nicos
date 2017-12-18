description = 'neutron camera'
group = 'optional'

#includes = ['base']
includes = []

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer = device('nicos.devices.tango.TimerChannel',
        description = 'timer for the Neutron camera',
        tangodevice = tango_base + 'sxccd/timer',
    ),
    camimage = device('nicos_mlz.frm2.devices.camera.CameraImage',
        description = 'image for the Neutron camera',
        tangodevice = tango_base + 'sxccd/image',
    ),
    cam = device('nicos.devices.generic.Detector',
        description = 'NeutronOptics camera',
        timers = ['camtimer'],
        monitors = [],
        counters = [],
        images = ['camimage'],
    ),
    tifformat = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I',
    ),
)
