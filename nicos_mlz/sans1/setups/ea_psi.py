#  -*- coding: utf-8 -*-

description = 'Multipurpose EA power supply'
group = 'optional'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/ea_ps'

devices = dict(
    ea_psi_curr = device('nicos.devices.tango.PowerSupply',
        description = 'Current regulated ea powersupply',
        tangodevice = '%s/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
