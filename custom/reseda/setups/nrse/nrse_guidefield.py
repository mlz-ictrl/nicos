#  -*- coding: utf-8 -*-

description = 'Guide field for NRSE mode'
group = 'lowlevel'

tango_base = 'tango://heinzinger.reseda.frm2:10000/box/heinzinger1'

devices = dict(
    guidefield = device('devices.tango.PowerSupply',
        description = 'Guide field power supply (current regulated)',
        tangodevice = '%s/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
