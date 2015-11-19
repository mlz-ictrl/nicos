description = 'QMesyDAQ detector devices'

group = 'lowlevel'

servername = 'SPODICTRL'

nameservice = 'spodictrl.spodi.frm2'

includes = []

# ;server CPU for mesytec psd (currently simulated on work station)
# SPODICTRL 1000
#
# MON1 500 qmesydaq.caress_object monitor1
# MON2 500 qmesydaq.caress_object monitor2
# TIM1 500 qmesydaq.caress_object timer	1
# EVENT 500 qmesydaq.caress_object event

nethost = 'spodisrv.spodi.frm2'

devices = dict(
    mon1 = device('devices.vendor.qmesydaq.QMesyDAQCounter',
                  description = 'QMesyDAQ Counter0',
                  tacodevice = '//%s/test/qmesydaq/counter0' % nethost,
                  type = 'monitor',
                 ),
    mon2 = device('devices.vendor.qmesydaq.QMesyDAQCounter',
                  description = 'QMesyDAQ Counter1',
                  tacodevice = '//%s/test/qmesydaq/counter1' % nethost,
                  type = 'monitor',
                 ),
    timer = device('devices.vendor.qmesydaq.QMesyDAQTimer',
                   description = 'QMesyDAQ Timer',
                   tacodevice = '//%s/test/qmesydaq/timer' % nethost,
                  ),
    qm_det = device('devices.vendor.qmesydaq.QMesyDAQImage',
                    description = 'QMesyDAQ MultiChannel Detector',
                    tacodevice = '//%s/test/qmesydaq/det' % nethost,
                    events = 'events',
                    timer = 'timer',
                    counters = [],
                    monitors = ['mon1', 'mon2'],
                    fileformats = [],
                    subdir = '',
                    readout = 'none',
                   ),
)

alias_config = {
}

startupcode = """
"""
