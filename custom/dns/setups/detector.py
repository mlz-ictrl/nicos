# -*- coding: utf-8 -*-

description = "Tof detector setup"

group = "optional"

includes = ['shutter', 'counter']

tango_host = 'tango://phys.dns.frm2:10000'

devices = dict(
               RawFileSaver = device('devices.fileformats.raw.RAWFileFormat',
                                     lowlevel = True),
               det = device("dns.detector.TofDetector",
                            description = "Tof detector",
                            tangodevice = '%s/dns/detector/1' % tango_host,
                            subdir = '.',
                            fileformats = ["RawFileSaver"],
                            expshutter = 'expshutter',
                            fpga = 'fpga',
                            readchannels = (0, 23),
                           ),
)

startupcode = "SetDetectors(det)"
