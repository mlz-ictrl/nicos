description = 'QMesyDAQ detector devices'

group = 'lowlevel'

servername = 'SPODICTRL'
nameservice = 'spodictrl.spodi.frm2'
caresspath = '/opt/caress'
toolpath = '/opt/caress'

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

#   mon1 = device('devices.vendor.qmesydaq.taco.Counter',
#                 description = 'QMesyDAQ Counter0',
#                 tacodevice = '//%s/test/qmesydaq/counter0' % nethost,
#                 type = 'monitor',
#                ),
#   mon2 = device('devices.vendor.qmesydaq.taco.Counter',
#                 description = 'QMesyDAQ Counter1',
#                 tacodevice = '//%s/test/qmesydaq/counter1' % nethost,
#                 type = 'monitor',
#                ),
#   timer = device('devices.vendor.qmesydaq.taco.Timer',
#                  description = 'QMesyDAQ Timer',
#                  tacodevice = '//%s/test/qmesydaq/timer' % nethost,
#                 ),
#   ctrs   = device('devices.vendor.qmesydaq.taco.Image',
#                   description = 'QMesyDAQ MultiChannel Detector',
#                   tacodevice = '//%s/test/qmesydaq/det' % nethost,
#                  ),
#   qm_det  = device('devices.generic.Detector',
#                    description = 'QMesyDAQ Detector',
#                    timers = ['timer'],
#                    counters = [],
#                    monitors = ['mon1', 'mon2'],
#                    images = ['ctrs'],
#                    fileformats = [],
#                    subdir = '',
#                   ),

    mon = device('devices.vendor.qmesydaq.caress.Counter',
                 description = 'HWB MON',
                 fmtstr = '%d',
                 type = 'monitor',
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % ('qmesydaq'),
                 # config = 'MON 116 11 0x1000000 1',
                 config = 'MON 500 qmesydaq.caress_object monitor1',
                 caresspath = caresspath,
                 toolpath = toolpath,
                 lowlevel = True,
                ),
    tim1 = device('devices.vendor.qmesydaq.caress.Timer',
                  description = 'HWB TIM1',
                  fmtstr = '%.2f',
                  unit = 's',
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % ('qmesydaq'),
                  # config = 'TIM1 116 11 0x1000000 2',
                  config = 'TIM1 500 qmesydaq.caress_object timer 1',
                  caresspath = caresspath,
                  toolpath = toolpath,
                  lowlevel = True,
                 ),
    image = device('devices.vendor.qmesydaq.caress.Image',
                   description = 'Image data device',
                   fmtstr = '%d',
                   pollinterval = 86400,
                   nameserver = '%s' % (nameservice,),
                   objname = '%s' % ('qmesydaq'),
                   # config = 'MON 116 11 0x1000000 1',
                   caresspath = caresspath,
                   toolpath = toolpath,
                   config = 'HISTOGRAM 500 qmesydaq.caress_object histogram 16'
                            ' 256 0',
                   lowlevel = True,
                  ),
    histogram = device('frm2.qmesydaqsinks.HistogramFileFormat',
                       description = 'Histogram data written via QMesyDAQ',
                       image = 'image',
                      ),
    listmode = device('frm2.qmesydaqsinks.ListmodeFileFormat',
                      description = 'Listmode data written via QMesyDAQ',
                      image = 'image',
                     ),
    adet = device('devices.generic.Detector',
                  description = 'Classical detector with single channels',
                  timers = ['tim1'],
                  monitors = ['mon'],
                  counters = [],
                  images = ['image'],
                  maxage = 3,
                  pollinterval = 0.5,
                  fileformats = ['listmode', 'histogram',],
                 ),
)
