description = 'Plug connector switch for neodry60E'

includes = []

group = 'optional'

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    valve_switch = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'plug connector switch for neodry60E',
        tangodevice = tango_base + 'switchbox/switch',
        mapping = {
            'on': 1,
            'off': 0
        }
    ),
)
