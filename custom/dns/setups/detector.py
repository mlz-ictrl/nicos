# -*- coding: utf-8 -*-

description = "DNS detector setup"
group = "lowlevel"

includes = ['counter']

sysconfig = dict(
    datasinks = ['conssink', 'filesink', 'daemonsink', 'DNSFileSaver'],
)

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    DNSFileSaver = device('dns.dnsfileformat.DNSFileFormat',
                          lowlevel = True,
                         ),
    dettof       = device('dns.detector.TofChannel',
                          description = 'TOF data channel',
                          tangodevice = tango_base + 'detector/1',
                          readchannels = (0, 23),
                          readtimechan = (0, 0),
                         ),
    det          = device('dns.detector.DNSDetector',
                          description = 'Tof detector',
                          timers = ['timer'],
                          monitors = ['mon0'],
                          images = ['dettof'],
                          flipper = 'flipper',
                         ),
)

startupcode = '''
SetDetectors(det)
'''
