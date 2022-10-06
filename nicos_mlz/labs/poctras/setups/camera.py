description = 'Camera devices'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/lima/zwo/'

sysconfig = dict(
    datasinks = ['image'],
)

devices = dict(
    cam = device('nicos.devices.vendor.lima.GenericLimaCCD',
        description = 'ZWO ASI camera',
        tangodevice = tango_base + 'cam1',
        visibility = (),
    ),
    timer = device('nicos.devices.vendor.lima.LimaCCDTimer',
        tangodevice = tango_base + 'cam1',
        visibility = (),
    ),
    camera = device('nicos.devices.generic.Detector',
        description = 'Camera base detector',
        images = ['cam'],
        timers = ['timer'],
    ),
    image = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data of camera',
        detectors = ['camera'],
        subdir = 'camera',
        filenametemplate = ['%(pointsamplecounter)08d.fits'],
    ),
    camtemp = device('nicos.devices.vendor.lima.ZwoTC',
        description = 'Temperature of the CCD sensor chip',
        tangodevice = tango_base + 'cooler',
        abslimits = (-30, 30),
        precision = 0.5,
        unit = 'degC',
    ),
)

startupcode = '''
SetDetectors(camera)
'''
