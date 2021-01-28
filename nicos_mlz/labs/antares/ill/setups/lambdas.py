description = 'Lambda power supplies'
group = 'optional'

tango_base = 'tango://127.0.0.1:10000/antares/'

devices = dict(
    I_lambda1 = device('nicos.devices.tango.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        precision = 0.04,
        timeout = 10,
    ),
)
