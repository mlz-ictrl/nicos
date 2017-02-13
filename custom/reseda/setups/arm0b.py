#  -*- coding: utf-8 -*-

description = 'Arm 0 B'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm0b_fwdp = device('devices.tango.AnalogInput',
        description = 'Forward power (B)',
        tangodevice = '%s/arm0/fwdp_b' % tango_base,
        fmtstr = '%.3f',
    ),
    arm0b_revp = device('devices.tango.AnalogInput',
        description = 'Reverse power (B)',
        tangodevice = '%s/arm0/revp_b' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0b_ag = device('devices.tango.AnalogInput',
        description = 'Temperature (B)',
        tangodevice = '%s/arm0/temp_b' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0b_coil1 = device('devices.tango.AnalogInput',
        description = 'Arm 0 (B) coil 1 temperature',
        tangodevice = '%s/iobox/plc_t_arm0bcoil1' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0b_coil2 = device('devices.tango.AnalogInput',
        description = 'Arm 0 (B) coil 2 temperature',
        tangodevice = '%s/iobox/plc_t_arm0bcoil2' % tango_base,
        fmtstr = '%.3f',
    ),
)
