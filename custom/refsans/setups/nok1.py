description = 'Nok1 setup'

nethost = '//refsanssrv.refsans.frm2/'

devices = dict(
        n1port = device('nicos.taco.io.AnalogInput',
                        tacodevice = nethost + 'test/wb_a/1_0',
                        lowlevel = True,
                       ),
        n1ref = device('nicos.taco.io.AnalogInput',
                        tacodevice = nethost + 'test/wb_a/1_6',
                        lowlevel = True,
                       ),
        n1obs = device('nicos.refsans.nok.Coder',
                      unit = 'mm',
                      fmtstr = '%.1f',
                      refhigh = 19.8,
                      reflow = 18.0,
                      refwarn = 17.0,
                      corr = 'mul',
                      mul = 0.996393,
                      off = -13.748035,
                      snr = 6505,
                      length = 250,
                      sensitivity = 3.856,
                      port = 'n1port',
                      ref = 'n1ref',
                      position = 'bottom',
                      ),
#        nok1 = device('nicos.refsans.nok.Nok', 
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
         )



