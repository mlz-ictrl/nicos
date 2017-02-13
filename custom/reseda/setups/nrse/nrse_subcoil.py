#  -*- coding: utf-8 -*-

description = 'Substraction coil for NRSE mode'
group = 'lowlevel'
excludes = ['mieze_subcoil']

tango_base = 'tango://heinzinger.reseda.frm2:10000/box/heinzinger'

devices = dict(
    subcoil_ps2 = device('devices.tango.PowerSupply',
        description = 'Current regulated powersupply 2',
        tangodevice = '%s2/curr' % tango_base,
        fmtstr = '%.4f',
    ),
    subcoil_ps3 = device('devices.tango.PowerSupply',
        description = 'Current regulated powersupply 3',
        tangodevice = '%s3/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
