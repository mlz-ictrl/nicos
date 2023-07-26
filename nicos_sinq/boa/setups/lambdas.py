description = 'Lambda power supplies'
group = 'optional'

#tango_base = 'tango://10.167.30.89:10000/antares/'
#tango_base = 'tango://antaresopc10.psi.ch:10000/antares/'
tango_base = 'tango://172.28.67.72:10000/antares/'
devices = dict(
    I_lambda1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        precision = 0.04,
        timeout = 10,
    ),
)
