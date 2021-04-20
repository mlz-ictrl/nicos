description = 'Lambda power supplies and polarity control'
group = 'optional'

excludes = ['lambdas']

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'
tango_base_beckhoff = 'tango://antareshw.antares.frm2:10000/antares/beckhoff02/beckhoff02_'

devices = dict(
    I_lambda1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        precision = 0.02,
        timeout = 10,
    ),
    Polarity_lambda1 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Polarity switch of Lambda 1' ,
        tangodevice = tango_base_beckhoff + 'out1',
        mapping = dict(Positive = 0, Negative = 1),
    ),
    I_lambda2 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 2',
        tangodevice = tango_base + 'lambda2/current',
        precision = 0.02,
        timeout = 10,
    ),
    Polarity_lambda2 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Polarity switch of Lambda 2' ,
        tangodevice = tango_base_beckhoff + 'out2',
        mapping = dict(Positive = 0, Negative = 1),
    ),
    I_lambda3 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 3',
        tangodevice = tango_base + 'lambda3/current',
        precision = 0.05,
        timeout = 10,
    ),
    Polarity_lambda3 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Polarity switch of Lambda 3' ,
        tangodevice = tango_base_beckhoff + 'out3',
        mapping = dict(Positive = 0, Negative = 1),
    ),
    I_lambda4 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 4',
        tangodevice = tango_base + 'lambda4/current',
        precision = 0.05,
        timeout = 10,
    ),
    Polarity_lambda4 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Polarity switch of Lambda 4' ,
        tangodevice = tango_base_beckhoff + 'out4',
        mapping = dict(Positive = 0, Negative = 1),
    ),
)
