description = 'tisane setup for SANS1'

includes = ['collimation', 'detector', 'sample_table_1', 'det1',
            'pressure', 'selector_tower', 'astrium', 'memograph',
            'manual', 'guidehall', 'outerworld', 'pressure_filter']

excludes = ['sans1']

group = 'basic'

nethost = 'sans1srv.sans1.frm2'
tangobase = 'tango://sans1hw.sans1.frm2:10000'

sysconfig = dict(
    datasinks = ['Histogram', 'Listmode',]
)

devices = dict(
    tisane_fc = device('devices.tango.Sensor',
                       description = "Frequency counter for chopper signal",
                       tangodevice = "%s/sans1/tisane/fc1_frequency" % tangobase,
                       unit = "Hz",
                      ),
    tisane_fg1 = device('sans1.tisane.Burst',
                        description = "Signal-generator for sample tisane signal",
                        tangodevice = "%s/sans1/tisane/fg1_burst" % tangobase,
                        frequency = 300,
                        amplitude = 5.0,
                        offset = 1.2,
                        shape = 'square',
                        duty = 50,
                        mapping = dict(On=1, Off=0),
                       ),
    tisane_fg2 = device('sans1.tisane.Burst',
                        description = "Signal-generator for detector tisane signal",
                        tangodevice = "%s/sans1/tisane/fg2_burst" % tangobase,
                        frequency = 600,
                        amplitude = 2.4,
                        offset = 1.3,
                        shape = 'square',
                        duty = 20,
                        mapping = dict(On=1, Off=0),
                       ),
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
