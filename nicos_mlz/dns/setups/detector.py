# -*- coding: utf-8 -*-

description = 'DNS detector setup'
group = 'lowlevel'

includes = ['counter']

sysconfig = dict(
    datasinks = ['LiveView'],
)

tango_base = 'tango://phys.dns.frm2:10000/dns/'

devices = dict(
    LiveView     = device('nicos.devices.datasinks.LiveViewSink',
                          lowlevel = True,
                         ),
    dettof       = device('nicos_mlz.dns.devices.detector.TofChannel',
                          description = 'TOF data channel',
                          tangodevice = tango_base + 'sistofdetector/1',
                          readchannels = (0, 23),
                          readtimechan = (0, 0),
                         ),
    det          = device('nicos_mlz.dns.devices.detector.DNSDetector',
                          description = 'Tof detector',
                          timers = ['timer'],
                          monitors = ['mon1'],
                          images = ['dettof'],
                          others = ['chopctr'],
                          flipper = 'flipper',
                         ),
)

extended = dict(
    poller_cache_reader = ['flipper']
)

startupcode = '''
SetDetectors(det)
'''
