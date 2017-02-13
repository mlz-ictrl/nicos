#  -*- coding: utf-8 -*-

description = 'Arm 0 A'
group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    arm0a_fwdp = device('devices.tango.AnalogInput',
        description = 'Forward power (A)',
        tangodevice = '%s/arm0/fwdp_a' % tango_base,
        fmtstr = '%.3f',
    ),
    arm0a_revp = device('devices.tango.AnalogInput',
        description = 'Reverse power (A)',
        tangodevice = '%s/arm0/revp_a' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0a_ag = device('devices.tango.AnalogInput',
        description = 'Temperature (A)',
        tangodevice = '%s/arm0/temp_a' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0a_coil1 = device('devices.tango.AnalogInput',
        description = 'Arm 0 (A) coil 1 temperature',
        tangodevice = '%s/iobox/plc_t_arm0acoil1' % tango_base,
        fmtstr = '%.3f',
    ),
    T_arm0a_coil2 = device('devices.tango.AnalogInput',
        description = 'Arm 0 (A) coil 2 temperature',
        tangodevice = '%s/iobox/plc_t_arm0acoil2' % tango_base,
        fmtstr = '%.3f',
    ),
)
