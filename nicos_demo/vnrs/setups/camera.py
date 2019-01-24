description = 'Camera devices'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/zwo/camera/'

sysconfig = dict(
    datasinks = ['image'],
)

devices = dict(
    cam = device('nicos.devices.generic.VirtualImage',
        description = 'ZWO ASI camera',
        fmtstr = '%d',
        sizes = (1024, 1024),
        lowlevel = True,
    ),
    timer = device('nicos.devices.generic.VirtualTimer',
        lowlevel = True,
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
    camtemp = device('nicos.devices.generic.VirtualTemperature',
        description = 'Temperature of the CCD sensor chip',
        speed = 6,
        abslimits = (-30, 30),
        precision = 0.5,
        fmtstr = '%.0f',
        unit = 'degC',
    ),
)

startupcode = '''
SetDetectors(camera)
'''
