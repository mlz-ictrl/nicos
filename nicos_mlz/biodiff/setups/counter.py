# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "lowlevel"

tango_base = "tango://phys.biodiff.frm2:10000/biodiff/"

devices = dict(
    timer = device("nicos_mlz.jcns.devices.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card timer channel",
                   tangodevice = tango_base + 'count/0',
                  ),
)
