description = 'tisane detector setup for SANS1'

group = 'lowlevel'

excludes = ['sans1_det']

nethost = 'sans1srv.sans1.frm2'

sysconfig = dict(
    datasinks = ['Histogram', 'Listmode']
)

devices = dict(
    det1 = device('nicos_mlz.sans1.devices.detector.GatedDetector',
        description = 'QMesyDAQ Image type Detector1',
        timers = ['det1_timer'],
        monitors = ['det1_mon1', 'det1_mon2', 'tisane_det_pulses'],
        images = ['det1_image'],
        #gates = ['tisane_fg2_det', 'tisane_fg1_sample'],
        #enablevalues = ['On', 'On'],
        #disablevalues = ['Off', 'Off'],
        gates = ['tisane_fg_multi'],
        #enablevalues = ['arm'],
        #disablevalues = ['off'],
    ),
    tisane_det_pulses = device('nicos.devices.generic.DeviceAlias',
        description = 'QMesyDAQ Counter2 (reference for tisane)',
        devclass = 'nicos.devices.generic.PassiveChannel',
        alias = 'det1_mon3',
    )
)

startupcode = '''
det1._attached_images[0].listmode = True
'''
