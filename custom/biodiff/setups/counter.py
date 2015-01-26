# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "ZEA-2 counter card setup"
group = "optional"

_TANGO_SRV = "phys.biodiff.frm2:10000"
_TANGO_URL = "tango://" + _TANGO_SRV + "/biodiff/count/"

devices = dict(
    timer = device("jcns.fpga.FPGATimerChannel",
                   description = "ZEA-2 counter card timer channel",
                   tangodevice = _TANGO_URL + '0',
                  ),
)
