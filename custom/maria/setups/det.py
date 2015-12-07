# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "basic"

includes = []

tango_base = "tango://phys.maria.frm2:10000/maria"

devices = dict(
    timer         = device("devices.generic.VirtualTimer",
                           lowlevel = True,
                          ),
    detimg        = device("maria.detector.DenexImage",
                           description = "Denex detector image",
                           tangodevice = tango_base + "/denex/detector",
                          ),
    det           = device("devices.generic.Detector",
                           description = "Denex detector",
                           timers = ["timer"],
                           images = ["detimg"],
                          ),
)

startupcode = "SetDetectors(det)"
