# -*- coding: utf-8 -*-

description = "Tof detector setup"

group = "optional"

includes = ['shutter', 'counter', 'coils']
excludes = ['detectortest']

tango_host = 'tango://phys.dns.frm2:10000'

devices = dict(
    DNSFileSaver = device('dns.dnsfileformat.DNSFileFormat',
                          lowlevel = True,
                         ),
    dettof       = device('dns.detector.TofChannel',
                          description = 'TOF data channel',
                          tangodevice = '%s/dns/detector/1' % tango_host,
                          readchannels = (0, 23),
                         ),
    det          = device('dns.detector.DNSDetector',
                          description = 'Tof detector',
                          timers = ['timer'],
                          monitors = ['mon0'],
                          images = ['dettof'],
                          flipper = 'flipper',
                          fileformats = ["DNSFileSaver"],
                          subdir = '.',
                         ),
)

startupcode = "SetDetectors(det)"
