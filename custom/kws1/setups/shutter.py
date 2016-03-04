# -*- coding: utf-8 -*-

description = "Beam shutter setup"
group = "lowlevel"

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    shutter_in  = device('devices.tango.DigitalInput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_in',
                         lowlevel = True,
                        ),
    shutter_set = device('devices.tango.DigitalOutput',
                         tangodevice = tango_base + 'fzjdp_digital/shutter_write',
                         lowlevel = True,
                        ),
    shutter     = device('kws1.shutter.Shutter',
                         description = 'shutter control',
                         output = 'shutter_set',
                         input = 'shutter_in',
                        ),
)
