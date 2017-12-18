description = 'polarity reversing relays'
group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    relay1 = device('nicos_mlz.mira.devices.beckhoff.NamedDigitalOutput',
        description = 'polarity switchover relay 1',
        tangodevice = tango_base + 'beckhoff/beckhoff1',
        startoffset = 0,
        mapping = {'off': 0,
                   'on': 1},
    ),
    relay2 = device('nicos_mlz.mira.devices.beckhoff.NamedDigitalOutput',
        description = 'polarity switchover relay 2',
        startoffset = 1,
        tangodevice = tango_base + 'beckhoff/beckhoff1',
        mapping = {'off': 0,
                   'on': 1},
    ),
)
