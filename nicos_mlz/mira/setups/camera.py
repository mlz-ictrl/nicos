description = 'neutron camera'
group = 'optional'

includes = ['base']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    camtimer = device('nicos.devices.tango.TimerChannel',
        description = 'timer for the Neutron camera',
        tangodevice = tango_base + 'sxccd/timer',
    ),
    camimage = device('nicos_mlz.devices.camera.CameraImage',
        description = 'image for the Neutron camera',
        tangodevice = tango_base + 'sxccd/image',
    ),
    camroi = device('nicos.devices.generic.RectROIChannel',
        description = 'ROI of the camera',
        roi = (0, 0, 768, 512),
    ),
    cam = device('nicos.devices.generic.Detector',
        description = 'NeutronOptics camera',
        timers = ['camtimer'],
        monitors = [],
        counters = ['camroi'],
        images = ['camimage'],
        postprocess = [
            ('camroi', 'camimage'),
        ],
    ),
    tifformat = device("nicos.devices.datasinks.TIFFImageSink",
        description = "Saves image data in TIFF format",
        filenametemplate = ["%(proposal)s_%(pointcounter)08d.tiff"],
        mode = "I",
    ),
)
