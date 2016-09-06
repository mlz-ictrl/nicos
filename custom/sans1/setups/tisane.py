description = 'tisane setup for SANS1'

includes = ['collimation', 'detector', 'sample_table_1', 'det1',
            'pressure', 'selector_tower', 'astrium', 'memograph',
            'manual', 'guidehall', 'outerworld', 'pressure_filter',
            'frequency']

excludes = ['sans1']

group = 'basic'

nethost = 'sans1srv.sans1.frm2'

sysconfig = dict(
    datasinks = ['Histogram', 'Listmode',]
)

devices = dict(
    det1    = device('devices.generic.GatedDetector',
                     description = 'QMesyDAQ Image type Detector1',
                     timers = ['det1_timer'],
                     counters = [],
                     monitors = ['det1_mon1', 'det1_mon2', 'tisane_det_pulses'],
                     images = ['det1_image'],
                     gates = ['tisane_fg2', 'tisane_fg1'],
                     enablevalues = ['On', 'On'],
                     disablevalues = ['Off', 'Off'],
                    ),
    tisane_det_pulses = device('devices.generic.DeviceAlias',
                               description = 'tisane detector channel',
                               devclass = 'devices.generic.PassiveChannel',
                               alias = 'det1_mon3',
                              )
)

startupcode = '''
det1._attached_images[0].listmode = True
'''
