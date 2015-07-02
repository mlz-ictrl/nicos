# -*- coding: utf-8 -*-

description = "Tof detector setup"

group = "optional"

includes = ['shutter', 'counter']
excludes = ['detector']

tango_host = 'tango://phys.dns.frm2:10000'

devices = dict(
    DNSFileSaver = device('dns.DNSFileFormat_onlyDet.DNSFileFormat_onlyDet_tof',
                          lowlevel = True,
                         ),
    dettest = device("dns.detector.TofDetectorBase",
                 description = "Tof detector",
                 tangodevice = '%s/dns/detector/1' % tango_host,
                 subdir = '.',
                 fileformats = ["DNSFileSaver"],
                 expshutter = 'expshutter',
                 timer = 'timer',
                 monitor = 'mon0',
                 readchannels = (0, 23),
                ),
)

startupcode = "SetDetectors(dettest)"
