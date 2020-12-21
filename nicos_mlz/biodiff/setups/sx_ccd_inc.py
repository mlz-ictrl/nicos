description = 'Starlight Xpress neutron camera'
group = 'optional'

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'

sysconfig = dict(
    datasinks = ['tifformat'],
)

devices = dict(
    sxccdtimer = device('nicos.devices.tango.TimerChannel',
        description = 'timer for the Neutron camera',
        tangodevice = tango_base + 'sxccd/timer',
    ),
    sxccd = device('nicos_mlz.devices.camera.CameraImage',
        description = 'image for the Neutron camera',
        tangodevice = tango_base + 'sxccd/image',
    ),
    sxccddet = device('nicos_mlz.biodiff.devices.detector.BiodiffDetector',
        description = 'NeutronOptics camera',
        timers = ['sxccdtimer'],
        monitors = [],
        counters = [],
        images = ['sxccd'],
        gammashutter = 'gammashutter',
        photoshutter = 'photoshutter',
    ),
    tifformat = device("nicos.devices.datasinks.TIFFImageSink",
        description = "Saves image data in TIFF format",
        filenametemplate = ["%(proposal)s_%(pointcounter)08d.tiff"],
        mode = "I",
        detectors = ['sxccddet'],
    ),
)

startupcode = '''
SetDetectors(sxccddet)
'''
