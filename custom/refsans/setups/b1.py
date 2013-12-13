NOK = 'B1'

description = '%s setup' % (NOK)

nok = NOK.lower()

nethost = 'refsanssrv.refsans.frm2'

includes = ['nokref',]

devices = {
        nok + 'portr' : device('devices.taco.io.AnalogInput',
                               description = 'Voltage input of the %s coder (reactor side)' % (NOK),
                               tacodevice = '//%s/test/wb_a/2_2' % (nethost,),
                               lowlevel = True,
                              ),
        nok + 'ports' : device('devices.taco.io.AnalogInput',
                               description = 'Voltage input of the %s coder (sample side)' % (NOK),
                               tacodevice = '//%s/test/wb_a/2_3' % (nethost,),
                               lowlevel = True,
                              ),
        nok + 'obsr'  : device('refsans.nok.Coder',
                               description = '%s potentiometer coder (reactor side)' % (NOK),
                               mul = 1.000022,
                               off = 20.953222,
                               snr = 7787,
                               length = 500,
                               sensitivity = 1.922,
                               port = '%sportr' % (nok,),
                               ref = 'nrefa2',
                              ),
        nok + 'obss'  : device('refsans.nok.Coder',
                               description = '%s potentiometer coder (sample side)' % (NOK),
                               mul = 0.999742,
                               off = 13.321479,
                               snr = 7785,
                               length = 500,
                               sensitivity = 1.922,
                               port = '%sports' % (nok,),
                               ref = 'nrefa2',
                              ),
#       nok1 = device('refsans.nok.Nok',
#                      unit = 'mm',
#                      fmtstr = '%.5f',
#                      bus = 'motorbus2',
#                      motor = nethost + 'test/nok1/ngm',
#                      encoder = nethost + 'test/nok1/nge',
#                      refswitch = nethost + 'test/nok1/ngsref',
#                      lowlimitswitch = [nethost + 'test/nok1/ngsll',],
#                      highlimitswitch = [nethost + 'test/nok1/ngshl',],
#                      #refpos = [-14.419, ],
#                      refpos = [-14.729 ], #JFM07_06_2010
#                      backlash = 2,
#                      posinclination = 0,
#                      neginclination = 0,
#                     ),
         }
