description = 'Multipurpose EA power supply'
group = 'optional'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/sans1/ea_ps'

devices = dict(
    ea_psi_curr = device('nicos.devices.entangle.PowerSupply',
        description = 'Current regulated ea powersupply',
        tangodevice = '%s/curr' % tango_base,
        fmtstr = '%.4f',
    ),
)
