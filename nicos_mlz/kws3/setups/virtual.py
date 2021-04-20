# -*- coding: utf-8 -*-

description = 'Mirror virtual motors'
group = 'optional'
display_order = 31

tango_base = 'tango://phys.kws3.frm2:10000/kws3/'
s7_motor = tango_base + 's7_motor/'

devices = dict(
    mir_sam_x = device('nicos.devices.entangle.Motor',
        description = 'virtual pair mir_x and sam_hub_x',
        tangodevice = s7_motor + 'mir_sam_x',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    mir_sam_y = device('nicos.devices.entangle.Motor',
        description = 'virtual pair mir_y and sam_hub_y',
        tangodevice = s7_motor + 'mir_sam_y',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    mir_sam_tilt = device('nicos.devices.entangle.Motor',
        description = 'virtual pair mir_tilt sam_hub_y',
        tangodevice = s7_motor + 'mir_sam_tilt',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    mir_sam_det = device('nicos.devices.entangle.Motor',
        description = 'virtual mir_y + mir_tilt + sam_hub_y + det_y',
        tangodevice = s7_motor + 'mir_sam_det',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.3f',
        lowlevel = True,
    ),
)
