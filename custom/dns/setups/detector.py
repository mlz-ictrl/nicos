# -*- coding: utf-8 -*-

description = "DNS detector setup"
group = "lowlevel"

includes = ['counter']

sysconfig = dict(
    datasinks = ['DNSFileSaver', 'YAMLSaver', 'LiveView'],
)

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    DNSFileSaver = device('dns.dnsfileformat.DNSFileSink',
                          lowlevel = True,
                         ),
    YAMLSaver    = device('dns.yamlformat.YAMLFileSink',
                          lowlevel = True,
                         ),
    LiveView     = device('devices.datasinks.LiveViewSink',
                          lowlevel = True,
                         ),
    dettof       = device('dns.detector.TofChannel',
                          description = 'TOF data channel',
                          tangodevice = tango_base + 'sistofdetector/1',
                          readchannels = (0, 23),
                          readtimechan = (0, 0),
                         ),
    det          = device('dns.detector.DNSDetector',
                          description = 'Tof detector',
                          timers = ['timer'],
                          monitors = ['mon1'],
                          images = ['dettof'],
                          flipper = 'flipper',
                         ),
)

startupcode = '''
SetDetectors(det)
'''
