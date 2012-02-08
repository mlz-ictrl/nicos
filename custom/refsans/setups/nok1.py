NOK = 'NOK3'
nok = NOK.lower()
nethost = '//refsanssrv.refsans.frm2/'

description = '%s setup' % (NOK)

devices = dict(
        nref1 = device('nicos.refsans.nok.CoderReference',
                       description = 'Reference voltage device for the NOK coders',
                       tacodevice = nethost + 'test/wb_a/1_6',
                       lowlevel = True,
                       refhigh = 19.8,
                       reflow = 18.0,
                       refwarn = 17.0,
                       ),

        nok1port = device('nicos.taco.io.AnalogInput',
                          description = 'Voltage input of the NOK1 coder',
                          tacodevice = nethost + 'test/wb_a/1_0',
                          lowlevel = True,
                         ),
        nok1obs = device('nicos.refsans.nok.Coder',
                         description = 'NOK1 potentiometer coder',
                         mul = 0.996393,
                         off = -13.748035,
                         snr = 6505,
                         sensitivity = 3.856,
                         port = 'nok1port',
                         ref = 'nref1',
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



