description = 'Test of some TANGO devices'

group = 'optional'

devices = dict(
    c = device('nicos.devices.tango.AnalogInput',
        description = 'A TANGO analogue input',
        tangodevice = 'tango://localhost:10000/A/a/1',
    ),
    o = device('nicos.devices.tango.CounterChannel',
        description = 'A TANGO counter',
        tangodevice = 'tango://localhost:10000/T/t/1',
        type = 'counter',
    ),
)
