NOK = 'NOK3'
nok = NOK.lower()
nethost = '//refsanssrv.refsans.frm2/'

description = '%s setup' % (NOK)

includes = ['nok1',]

devices = {
        nok + 'portr' : device('nicos.taco.io.AnalogInput',
                               description = 'Voltage input of the %s coder (reactor side)' % (NOK),
                               tacodevice = nethost + 'test/wb_a/1_3',
                               lowlevel = True,
                              ),
        nok + 'ports' : device('nicos.taco.io.AnalogInput',
                               description = 'Voltage input of the %s coder (sample side)' % (NOK),
                               tacodevice = nethost + 'test/wb_a/1_4',
                               lowlevel = True,
                              ),
        nok + 'obsr'  : device('nicos.refsans.nok.Coder',
                               description = '%s potentiometer coder (reactor side)' % (NOK),
                               mul = 0.997962,
                               off = 21.830175,
                               snr = 6507,
                               sensitivity = 3.846,
                               port = nok + 'portr',
                               ref = 'nref1',
                              ),
        nok + 'obss'  : device('nicos.refsans.nok.Coder',
                               description = '%s potentiometer coder (sample side)' % (NOK),
                               mul = 1.003196,
                               off = 10.409698,
                               snr = 6506,
                               sensitivity = 3.854,
                               port = nok + 'ports',
                               ref = 'nref1',
                              ),
#       nok1 = device('nicos.refsans.nok.Nok', 
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



