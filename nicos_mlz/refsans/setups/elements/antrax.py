description = 'Antrax plug switching box'

group = 'plugplay'

tango_base = 'tango://antrax01.refsans.frm2.tum.de:10000/'

devices = dict(
    antrax = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Plug switching device',
        tangodevice = tango_base + 'box/switchbox/switch',
        mapping = {
            'off': 0,
            'on': 1,
        },
    ),
)
