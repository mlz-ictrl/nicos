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
    det = device("dns.detector.TofDetector",
                 description = "Tof detector",
                 tangodevice = '%s/dns/detector/1' % tango_host,
                 subdir = '.',
                 fileformats = ["DNSFileSaver"],
                 expshutter = 'expshutter',
                 timer = 'timer',
                 flipper = 'flipper',
                 monitor = 'mon0',
                 readchannels = (0, 23),
                ),
)

startupcode = "SetDetectors(det)"
