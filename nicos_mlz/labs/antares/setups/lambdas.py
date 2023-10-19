description = 'Lambda power supplies'
group = 'optional'

tango_base = 'tango://localhost:10000/antares/'

devices = dict(
    I_lambda1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        precision = 0.04,
        timeout = 10,
    ),
)
