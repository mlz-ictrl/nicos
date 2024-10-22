description = 'Netio PDU'

group = 'optional'

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    outlet1 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'outlet 1',
        tangodevice = tango_base + 'netio/outlet1',
        pollinterval = 2,
        maxage = 5,
        mapping = {
            'on': 1,
            'off': 0,
        },
    ),
    outlet2 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'outlet 2',
        tangodevice = tango_base + 'netio/outlet2',
        pollinterval = 2,
        maxage = 5,
        mapping = {
            'on': 1,
            'off': 0,
        },
    ),
    outlet3 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'outlet 3',
        tangodevice = tango_base + 'netio/outlet3',
        pollinterval = 2,
        maxage = 5,
        mapping = {
            'on': 1,
            'off': 0,
        },
    ),
    outlet4 = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'outlet 4',
        tangodevice = tango_base + 'netio/outlet4',
        pollinterval = 2,
        maxage = 5,
        mapping = {
            'on': 1,
            'off': 0,
        },
    ),
)
