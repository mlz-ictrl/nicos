description = 'sans1 detector setup'

group = 'lowlevel'

excludes = ['tisane_det']

sysconfig = dict(
    datasinks = ['Histogram']
)

devices = dict(
    det1 = device('nicos_mlz.sans1.devices.detector.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['det1_timer'],
        monitors = ['det1_mon1', 'det1_mon2'],
        images = ['det1_image'],
        liveinterval = 30.0,
    ),
)

startupcode = '''
det1._attached_images[0].listmode = False
'''
