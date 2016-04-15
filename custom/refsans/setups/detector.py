description = 'devices for fast detector using comtec p7888 for REFSANS'

# to be included by refsans?
group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test/fast' % nethost

sysconfig = dict(
    datasinks = ['comtec_sink'],
)

devices = dict(
    fastctr_a = device('refsans.detector.ComtecCounter',
                       description = "Channel A of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_a' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_b = device('refsans.detector.ComtecCounter',
                       description = "Channel B of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_b' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_c = device('refsans.detector.ComtecCounter',
                       description = "Channel C of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_c' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_d = device('refsans.detector.ComtecCounter',
                       description = "Channel D of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_d' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_e = device('refsans.detector.ComtecCounter',
                       description = "Channel E of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_e' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_f = device('refsans.detector.ComtecCounter',
                       description = "Channel F of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_f' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_g = device('refsans.detector.ComtecCounter',
                       description = "Channel G of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_g' % tacodev,
                       lowlevel = True,
                      ),
    fastctr_h = device('refsans.detector.ComtecCounter',
                       description = "Channel H of Comtep P7888 Fast Counter",
                       tacodevice = '%s/rate_h' % tacodev,
                       lowlevel = True,
                      ),
    comtec_sink     = device('refsans.detector.ComtecHeaderSink',
                             description = 'Copies image data and saves header',
                             lowlevel = True,
                             detector = 'comtec_timer',
                            ),
    comtec_timer    = device('refsans.detector.ComtecTimer',
                             description = 'Comtec P7888 Fast System: Timer channel',
                             tacodevice = '%s/detector' % tacodev,
                            ),
    comtec_filename = device('refsans.detector.ComtecFilename',
                             description = 'Comtec P7888 Fast System: Filename',
                             tacodevice = '%s/detector' % tacodev,
                            ),
    comtec          = device('devices.generic.Detector',
                             description = "detector, joining all channels",
                             timers = ['comtec_timer'],
                             images = [],
                             # counters = ['fastctr_%c'%c for c in 'abcdefgh'],
                             others = ['comtec_filename'],
                            ),
)

startupcode = '''
SetDetectors(comtec)
'''
