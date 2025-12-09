description = 'sans1 detector setup'

group = 'lowlevel'

includes = ['alias_det1']

excludes = ['tisane_det']

sysconfig = dict(
    # datasinks = ['Histogram'],
)

devices = dict(
    sans_det1 = device('nicos_mlz.sans1.devices.detector.Detector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['det1_timer'],
        monitors = ['det1_mon1', 'det1_mon2'],
        images = ['det1_image'],
        liveinterval = 30.0,
    ),
)

alias_config = {
    'det1': {'sans_det1': 100}
}

startupcode = '''
# det1._attached_images[0].listmode = False
'''
