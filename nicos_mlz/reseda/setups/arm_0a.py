#  -*- coding: utf-8 -*-

description = 'Arm 0 A'
group = 'lowlevel'
includes = ['cbox_0a']

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    T_arm0a_coil1 = device('nicos.devices.tango.AnalogInput',
        description = 'Arm 0 (A) coil 1 temperature',
        tangodevice = '%s/iobox/plc_t_arm0acoil1' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0a_coil2 = device('nicos.devices.tango.AnalogInput',
        description = 'Arm 0 (A) coil 2 temperature',
        tangodevice = '%s/iobox/plc_t_arm0acoil2' % tango_base,
        fmtstr = '%.3f',
    ),
)
