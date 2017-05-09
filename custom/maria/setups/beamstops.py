# -*- coding: utf-8 -*-

description = "Beamstops setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"

devices = dict(
    bsd = device("devices.tango.Motor",
        description = "Beamstops/BSD",
        tangodevice = tango_s7 + "/bsd",
        precision = 0.01,
    ),
    bs1_rot = device("devices.tango.Motor",
        description = "Beamstops/Ref_BSD 1 rotation",
        tangodevice = tango_s7 + "/bs1_rot",
        precision = 0.01,
    ),
    bs1_trans = device("devices.tango.Motor",
        description = "Beamstops/Ref_BSD 1 translation",
        tangodevice = tango_s7 + "/bs1_trans",
        precision = 0.01,
    ),
    bs2_rot = device("devices.tango.Motor",
        description = "Beamstops/Ref_BSD 2 rotation",
        tangodevice = tango_s7 + "/bs2_rot",
        precision = 0.01,
    ),
    bs2_trans = device("devices.tango.Motor",
        description = "Beamstops/Ref_BSD 2 translation",
        tangodevice = tango_s7 + "/bs2_trans",
        precision = 0.01,
    ),
    sc = device("devices.tango.Motor",
        description = "Sample changer",
        tangodevice = tango_s7 + "/sam_changer",
        precision = 0.01,
    )
)
