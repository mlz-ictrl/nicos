#  -*- coding: utf-8 -*-

description = 'Arm 0 B'
group = 'lowlevel'
includes = ['cbox_0b']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    T_arm0b_coil1 = device('nicos.devices.tango.AnalogInput',
        description = 'Arm 0 (B) coil 1 temperature',
        tangodevice = '%s/iobox/plc_t_arm0bcoil1' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0b_coil2 = device('nicos.devices.tango.AnalogInput',
        description = 'Arm 0 (B) coil 2 temperature',
        tangodevice = '%s/iobox/plc_t_arm0bcoil2' % tango_base,
        fmtstr = '%.3f',
    ),
)
